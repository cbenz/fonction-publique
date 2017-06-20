######################################################################################################################## 
######################################## TRAJECTORIES in ADJOINT TECHNIQUE CORPS ######################################
######################################################################################################################## 


#### 0. Initialisation ####

rm(list = ls()); gc()

# path
place = "ippS"
if (place == "ippS"){
  data_path = "M:/CNRACL/output/"
  git_path =  'U:/Projets/CNRACL/fonction-publique/fonction_publique/'
}
if (place == "ippL"){
  data_path = "M:/CNRACL/output/"
  git_path =  'C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/'
}
if (place == "mac"){
  data_path = "/Users/simonrabate/Desktop/data/CNRACL/"
  git_path =  '/Users/simonrabate/Desktop/IPP/CNRACL/fonction_publique/'
}
fig_path = paste0(git_path,"ecrits/modelisation_carriere/Figures/")
tab_path = paste0(git_path,"ecrits/modelisation_carriere/Tables/")

### Loading packages and functions ###
source(paste0(git_path, 'modelisation/OutilsCNRACL.R'))

# Read csv

filename = paste0(data_path,"clean_data_finalisation/data_ATT_2002_2015_with_filter_on_etat_at_exit_and_change_to_filter_on_etat_quarterly.csv")
data_long = read.csv(filename)  

### 0. WoD ####

# Data with one line by ech transition.

# Format bolean                     
to_bolean = c("right_censored", "left_censored", "exit_status")
data_long[, to_bolean] <- sapply(data_long[, to_bolean], as.logical)


data_long$trim = data_long$quarter
data_long$exit_next = ifelse(data_long$annee == data_long$last_y_observed_in_grade, 1, 0)
data_long$exit_next[which(data_long$right_censored == T)] = 0


# Count echelon transition
data_long$bef_ech <-ave(data_long$echelon, data_long$ident, FUN=shiftm1)
data_long$change_ech <- ifelse((data_long$echelon != data_long$bef_ech & !is.na(data_long$bef_ech)), 1, 0)
data_long$change_ech[which(is.na(data_long$change_ech))] = 1

data_long$year_change = data_long$annee*data_long$change_ech

data_long$cumsum  <- ave(data_long$change_ech ,data_long$ident, FUN=cumsum)
data_long$tot     <- ave(data_long$change_ech,data_long$ident,FUN=sum)

# Drop first and last transition
data = data_long[-which(data_long$cumsum == 0 | data_long$cumsum == data_long$tot),]

# Keep only first transition 
data_first = data[which(data$cumsum == 1 & data$tot >1 ),]
data_first$a       <- 1
data_first$dur_ech <- ave(data_first$a, data_first$ident ,FUN=sum)
data_first = data_first[!duplicated(data_first$ident),]

# With entering echelon in 2011
data_first = data_first[which(data_first$year_change == 2011),]

data_TTH1 = data_first[which(data_first$c_cir_2011 == "TTH1"),]
data_TTH2 = data_first[which(data_first$c_cir_2011 == "TTH2"),]
data_TTH3 = data_first[which(data_first$c_cir_2011 == "TTH3"),]

data_TTH3 = data_first[which(data_first$c_cir_2011 == "TTH3" & data_first$next_grade == "TTH4"),]

subdata = data_TTH3
dur_ech = seq(1:15)
dist_dur_ech = matrix(ncol = length(dur_ech), nrow = 5)
for (t in 1:length(dur_ech))
{
dist_dur_ech[1,t] = length(which(subdata$dur_ech == dur_ech[t] & subdata$echelon == 1))/length(which(subdata$echelon == 1))
dist_dur_ech[2,t] = length(which(subdata$dur_ech == dur_ech[t] & subdata$echelon  >= 2 & subdata$echelon <= 3))/length(which(subdata$echelon  >= 2 & subdata$echelon <= 3))
dist_dur_ech[3,t] = length(which(subdata$dur_ech == dur_ech[t] & subdata$echelon  >= 4 & subdata$echelon <= 6))/length(which(subdata$echelon  >= 4 & subdata$echelon <= 6))  
dist_dur_ech[4,t] = length(which(subdata$dur_ech == dur_ech[t] & subdata$echelon  >= 7))/length(which(subdata$echelon  >= 7))
}  


cond = c(4, 6, 8, 12)
col1 = c(rep("cadetblue2", 4-1), "cadetblue4", rep("cadetblue2", 15-4))
col2 = c(rep("cadetblue2", 6-1), "cadetblue4", rep("cadetblue2", 15-6))
col3 = c(rep("cadetblue2", 8-1), "cadetblue4", rep("cadetblue2", 15-8))
col4 = c(rep("cadetblue2", 12-1), "cadetblue4", rep("cadetblue2", 15-12))
#pdf(paste0(fig_path,"distrib_an_aff.pdf"))
layout(matrix(c(1,2,3), nrow=1,ncol=3, byrow=TRUE))

labels = c(NA, 6, NA, 12, NA, 18, NA, 24, NA, 30, NA, 36, NA, 42, NA)
par(mar=c(5,4.1,2,0.2))
barplot(dist_dur_ech[2,],ylab="",xlab="", col = col2, names.arg = labels, main = "2<= Level <=3", font.axis = 2,cex.names = 1.3, cex.axis =  1)
barplot(dist_dur_ech[3,],ylab="",xlab="Duration (in month)", col = col3, names.arg = labels, main = " 4<= Level <=6", font.axis = 2,cex.names = 1.3, cex.axis =  1, cex.lab = 1.5)
subtitle("Duration (in month)")
barplot(dist_dur_ech[4,],ylab="",xlab="", col = col4, names.arg = labels, main = "Level >= 7", , font.axis = 2,cex.names = 1.3, cex.axis =  1)

# Check individus
i = 2
test = data_TTH3
indiv = test$ident[which(test$echelon == 7 & test$dur_ech == 6)][i]
var = c("ident", "c_cir", "annee", "trim", "echelon", "ib4", "etat","last_y_observed_in_grade")
View(data_long[which(data_long$ident == indiv),var])

