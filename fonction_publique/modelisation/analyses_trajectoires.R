######################################################################################################################## 
######################################## TRAJECTORIES in ADJOINT TECHNIQUE CORPS ######################################
######################################################################################################################## 


#### 0. Initialisation ####


# path
place = "mac"
if (place == "ipp"){
data_path = "M:/CNRACL/output/"
git_path =  'U:/Projets/CNRACL/fonction-publique/fonction_publique/'
}
if (place == "mac"){
  data_path = "/Users/simonrabate/Desktop/data/CNRACL/"
  git_path =  '/Users/simonrabate/Desktop/IPP/CNRACL/fonction_publique/'
}
fig_path = paste0(git_path,"ecrits/modelisation_carriere/Figures/")


                  
  
  ### Loading packages and functions ###
source(paste0(git_path, 'modelisation/OutilsCNRACL.R'))


                  

# Read csv
main = read.csv(paste0(data_path,"corpsAT.csv"))

ident = unique(main$ident)
sub = sample(ident, 10000)
sub_data = main[which(is.element(main$ident, sub)), ]

data = sub_data

#### I. WOD ####
data$libemploi = as.character(data$libemploi)
data$c_neg = as.numeric(format(data$c_neg))
data$c_neg[which(is.na(data$c_neg))] <- 0

# List of AT neg
list_neg = c(793, 794, 795, 796)
# First/last
data$a     <- 1
data$b     <- ave(data$a,data$ident,FUN=cumsum)
data$c     <- ave(data$a,data$ident,FUN=sum)
data$first <- ifelse(data$b==1,1,0)
data$last  <- ifelse(data$b==data$c,1,0)
data <- data[, !names(data) %in% c('a', 'b', 'c')]
# AT variables
data$ind_AT = ifelse(is.element(data$c_neg, list_neg), 1, 0) 
data$count_AT = ave(data$ind_AT, data$ident, FUN = sum)
# Changing grades variable
data$bef_neg  <-ave(data$c_neg, data$ident, FUN=shiftm1)
data$bef2_neg <-ave(data$c_neg, data$ident, FUN=shiftm2)
data$next_neg <-ave(data$c_neg, data$ident, FUN=shift1)
data$change_neg_bef  <- ifelse(data$c_neg == data$bef_neg, 0, 1)
data$change_neg_bef2 <- ifelse(data$c_neg == data$bef_neg | data$c_neg == data$bef2_neg, 0, 1)
data$change_neg_next <- ifelse(data$c_neg == data$next_neg, 0, 1)
# Ind libemploi 
data$ind_lib = ifelse(data$libemploi == '', 0, 1)
data$count_lib = ave(data$ind_lib, data$ident, FUN = sum)
data$bef_ind_lib <-ave(data$ind_lib, data$ident, FUN=shiftm1)
data$bef2_ind_lib <-ave(data$ind_lib, data$ident, FUN=shiftm2)
data$next_ind_lib <-ave(data$ind_lib, data$ident, FUN=shift1)
# Lib without AT
data$diff = data$count_lib - data$count_AT
# Ind missing echelon 
data$missing_ech = ifelse(is.na(data$echelon) & data$libemploi != '', 1, 0)
data$count_missing_ech = ave(data$missing_ech, data$ident, FUN = sum)



## Cleaned data: 
# - No missing lib (when ib not 0)
# - No decreasing ib
# - No missing NEG 
# - No NA echelon. 


list3 = data$ident[which(data$c_neg == 0 & data$libemploi != '')]
list4 = data$ident[which(is.na(data$echelon))]
list = unique(union(list3,list4))
data_cleaned = data[which(!is.element(data$ident, list)),]




#### II.1 Descriptive statistics ####


#### II.1 General statistics on the AT population ####
`
# Proportion of time spent in AT corps 
nb_AT = tapply(data$ind_AT, data$ident, FUN = sum)
nb_lib = tapply(data$ind_lib, data$ident, FUN = sum)
rel = nb_AT/nb_lib
hist(rel)
hist(nb_lib)
table(nb_lib, nb_AT)

# Missing echelon
mis_ech =  tapply(data$missing_ech, data$ident, FUN = sum)
table(mis_ech)
hist(mis_ech)
# Aller-retour dans les corps

data
data_all = data[which(data$count_AT == 9 & data$count_lib >= 5), ]



#### II.2 Entry and exit neg ####

# TODO: échelon d'entrée, de sortie, durée passée dans le corps

list_neg = c(793, 794, 795, 796)
table_entry = matrix(ncol = length(list_neg), nrow = 9)
table_exit  = matrix(ncol = length(list_neg), nrow = 9)

data_entry = data[which(data$change_neg_bef ==1  & data$annee>2007),]
data_entry$bef_neg[which(data_entry$bef_neg == 0 & data_entry$lag_ind_lib == 1)] = 999
data_entry$bef_neg[which(data_entry$bef_neg == 0 & data_entry$lag_ind_lib == 0)] = 888

data_exit = data[which(data$change_neg_next ==1  & data$annee<2015),]
data_exit$next_neg[which(data_exit$next_neg == 0 & data_exit$next_ind_lib == 1)] = 999
data_exit$next_neg[which(data_exit$next_neg == 0 & data_exit$next_ind_lib == 0)] = 888

for (n in 1:length(list_neg))
{
list = which(data_entry$c_neg == list_neg[n]) 
# From AT neg
for (n2 in 1:length(list_neg))
{
list2 = which(data_entry$bef_neg == list_neg[n2])
table_entry[(n2),n] = length(intersect(list, list2))/length(list)  
}
# From other known neg
list3 = which(!is.element(data_entry$bef_neg, cbind(888, 999, list_neg)))
table_entry[5,n] = length(intersect(list, list3))/length(list)  
# From missing neg
list4 = which(data_entry$bef_neg == 999)
table_entry[6,n] = length(intersect(list, list4))/length(list)  
# From missing libemploi
list5 = which(data_entry$bef_neg == 888)
table_entry[7,n] = length(intersect(list, list5))/length(list)  
# Total: 
table_entry[8,n] = sum(table_entry[1:7,n])

## Exit
list = which(data_exit$c_neg == list_neg[n]) 
# To AT neg
for (n2 in 1:length(list_neg)){
list2 = which(data_exit$next_neg == list_neg[n2])
table_exit[(n2),n] = length(intersect(list, list2))/length(list)  
}
# To other known neg
list3 = which(!is.element(data_exit$next_neg, cbind(888, 999, list_neg)))
table_exit[5,n] = length(intersect(list, list3))/length(list)  
# To missing neg
list4 = which(data_exit$next_neg == 999)
table_exit[6,n] = length(intersect(list, list4))/length(list)  
# To missing libemploi
list5 = which(data_exit$next_neg == 888)
table_exit[7,n] = length(intersect(list, list5))/length(list)  
# Total: 
table_exit[8,n] = sum(table_exit[1:7,n])
}


colnames(table) <- c("AT2", "AT1", "ATP2", "ATP1")
rownames(table) <- c("Nb obs", "Libell? n-1 manquant", "NEG n-1 = AT2", "NEG n-1 = AT1", "NEG n-1 = ATP2", "NEG n-1 = ATP1",
                    "NEG n-1 = autres", "NEG n-1 = manquant", "total")
table<-desc
print(xtable(table,align="l|cccc",nrow = nrow(table), ncol=ncol(table)+1, byrow=T),
      hline.after=c(0,1,9), sanitize.text.function=identity,size="\\footnotesize", only.contents=T)


#### II.3 Distribution of time spent in corps and echelon ####

data_all = data[which(data$count_AT == 9 & data$count_lib == 9 & data$count_missing_ech == 0), ]

# Distribution de l'échelon à l'entré dans corps
entry_echelon_AT2 = data$echelon[which(data$change_neg_bef2 ==1  & 
                                       data$c_neg == list_neg[1] & 
                                       data$annee > 2008)] 

View(data[which(is.element(data$ident, data$ident[which(data$change_neg_bef2 ==1  & 
                                                          data$c_neg == list_neg[1] & 
                                                          data$annee > 2008)])),])

View(data[which(is.element(data$ident, data$ident[which(data$change_neg_bef2 ==1  &
                           data$bef_ind_lib == 0 & data$bef2_ind_lib == 0 &                               
                           data$c_neg == list_neg[1] & data$annee > 2008)])),])
                  
                  
table(entry_echelon_AT2)

#### II.3 Distribution of destination when eligible ####

