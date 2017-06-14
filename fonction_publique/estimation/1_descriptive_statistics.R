
library(xtable)



######## Descriptive statistics ########


source(paste0(wd, "0_work_on_data.R"))
datasets = load_and_clean("M:/CNRACL/output/clean_data_finalisation", "/data_ATT_2002_2015_2.csv")
data_id = datasets[[1]]
data_max = datasets[[2]]
data_min = datasets[[3]]



## I. Sample description ####

## I.1 Sample  ####
table_count = matrix(ncol = 5, nrow = 2)
table_count[1,1] = length(unique(data_id$ident))
table_count[2,1] = 100
table_count[1,2:5] = format(round(as.data.frame(table(data_id$c_cir_2011))[1:4,2]))
table_count[2, 2:5] = format(round(as.data.frame(table(data_id$c_cir_2011))[1:4,2]/length(unique(data_id$ident))*100,1),1)
colnames(table_count) = c("All", "TTH1","TTH2", "TTH3", "TTH4")
rownames(table_count) = c('\\Number of agents', "\\% share of ATT population")

print(xtable(table_count,align="lccccc",nrow = nrow(table), ncol=ncol(table_censoring)+1, byrow=T, digits = 3),
      sanitize.text.function=identity,size="\\footnotesize", 
      only.contents=F, include.colnames = T)

## I.2 Censoring ####

data_id$right = as.numeric(data_id$right_censored)
data_id$left = as.numeric(data_id$left_censored)

mean_right <- aggregate(data_id$right, by = list(data_id$c_cir_2011), FUN=mean)    
mean_left  <- aggregate(data_id$left,  by = list(data_id$c_cir_2011), FUN=mean)    

table_censoring = matrix(ncol = 5, nrow = 2)
table_censoring[1,1] = mean(data_id$right)
table_censoring[1,2:5] = mean_right$x
table_censoring[2,1] = mean(data_id$left)
table_censoring[2,2:5] = mean_left$x

colnames(table_censoring) = c("All", "TTH1","TTH2", "TTH3", "TTH4")
rownames(table_censoring) = c('\\% right-censored', "\\% left-censored")

print(xtable(table_censoring,align="lccccc",nrow = nrow(table), ncol=ncol(table_censoring)+1, byrow=T, digits = 3),
      sanitize.text.function=identity,size="\\footnotesize", 
      only.contents=F, include.colnames = T)


figpath = "Q:/CNRACL/Slides/Graphiques"

## 1.3 Année d'affilation ####

subdata = data_id[which(data_id$left_censored == F),]
time = 2001:2011
prop_entry = matrix(ncol = length(time), nrow = 5)
for (t in 1:length(time))
{
prop_entry[1,t] = length(which(subdata$an_aff == time[t]))/length(subdata$an_aff)  
prop_entry[2,t] = length(which(subdata$an_aff == time[t] & subdata$c_cir_2011 == "TTH1"))/length(subdata$an_aff[which(subdata$c_cir_2011 == "TTH1")])    
prop_entry[3,t] = length(which(subdata$an_aff == time[t] & subdata$c_cir_2011 == "TTH2"))/length(subdata$an_aff[which(subdata$c_cir_2011 == "TTH2")])    
prop_entry[4,t] = length(which(subdata$an_aff == time[t] & subdata$c_cir_2011 == "TTH3"))/length(subdata$an_aff[which(subdata$c_cir_2011 == "TTH3")])    
prop_entry[5,t] = length(which(subdata$an_aff == time[t] & subdata$c_cir_2011 == "TTH4"))/length(subdata$an_aff[which(subdata$c_cir_2011 == "TTH4")])    
}  

pdf(paste0(fig_path,"distrib_an_aff.pdf"))
layout(matrix(c(1,2,3,4), nrow=2,ncol=2, byrow=TRUE), heights=c(3,3))
par(mar=c(2.5,4.1,1.3,0.2))
barplot(prop_entry[2,],ylab="Proportion d'entrée",xlab="Année", col = "darkcyan", names.arg = time, main = "TTH1")
barplot(prop_entry[3,],ylab="Proportion d'entrée",xlab="Année", col = "darkcyan", names.arg = time, main = "TTH2")
barplot(prop_entry[4,],ylab="Proportion d'entrée",xlab="Année", col = "darkcyan", names.arg = time, main = "TTH3")
barplot(prop_entry[5,],ylab="Proportion d'entrée",xlab="Année", col = "darkcyan", names.arg = time, main = "TTH4")
dev.off()





## II. Graphical evidence on exit grade ####

### II.1 Functions ####

# Hazard by duration in grade
hazard_by_duree = function(data, save = F, corps = F)
{
  grade = seq(1, 12)
  hazard   = numeric(length(grade))
  effectif = numeric(length(grade))
  
  for (g in 1:length(grade))
  {
  hazard[g]   = length(which(data$time ==  grade[g] & data$exit_status2 == 1))/length(which(data$time == grade[g]))
  effectif[g] = length(which(data$time == grade[g]))
  }  
  par(mar = c(5,5,2,5))
  xlabel = ifelse(corps, "Duration in corps", "Duration in grade")
  plot(grade, hazard, type ="l", lwd = 3, xlab = xlabel, ylab = "Hazard rate", col = "darkcyan")
  par(new = T)
  plot(grade, effectif, type ="l", lty = 2, lwd = 2, axes=F, xlab=NA, ylab=NA)
  axis(side = 4)
  mtext(side = 4, line = 3, 'Effectifs')
  legend("topleft", legend = c("Hazard", "Nb obs."), lwd = 3, lty = c(1,3), col = c("darkcyan", "black"), cex = 1.1)
  
}  

# Hazard by echelon
hazard_by_ech = function(data, save = F)
{
  ech = 1:12
  hazard = numeric(length(ech))
  effectif = numeric(length(ech))
  for (e in 1:length(ech))
  {
  hazard[e] =   length(which(data$echelon == ech[e] & data$exit_status2 == 1))/length(which(data$echelon == ech[e]))
  effectif[e] = length(which(data$echelon == ech[e]))
  }  

  par(mar = c(5,5,2,5))
  plot(ech, hazard, type ="l", lwd = 3, xlab = "Echelon", ylab = "Hazard rate", col = "darkcyan")
  par(new = T)
  plot(ech, effectif, type ="l", lty = 2, lwd = 2, axes=F, xlab=NA, ylab=NA)
  axis(side = 4)
  mtext(side = 4, line = 3, 'Effectifs')
  legend("topleft", legend = c("Hazard", "Nb obs."), lwd = 3, lty = c(1,3), col = c("darkcyan", "black"), cex = 1.1)
}  



# Distance to thresholds
hazard_by_distance = function(data, save = F, type = "choix", colors = c("black", "grey", "darkcyan"))
{
  if (type == "choix"){data$cond_grade = data$D_choice ; data$cond_ech = data$E_choice}
  if (type == "exam") {data$cond_grade = data$D_exam ; data$cond_ech = data$E_exam}
  
  data$dist_grade =  data$time  - data$cond_grade
  data$dist_echelon = data$echelon - data$cond_ech
  data$dist_both = pmin(data$dist_grade, data$dist_echelon)
  
  values = (min(min(data$dist_grade), min(data$dist_echelon), min(data$dist_both)):
              min(max(data$dist_grade), max(data$dist_echelon), max(data$dist_both)))
  hazards = matrix(ncol = length(values), nrow = 3)
  
  for (v in 1:length(values))
  {
    hazards[1,v]  = length(which(data$dist_grade  == values[v] & data$exit_status2 == 1))/length(which(data$dist_grade  == values[v]))
    hazards[2,v]  = length(which(data$dist_echelon  == values[v] & data$exit_status2 == 1))/length(which(data$dist_echelon  == values[v]))
    hazards[3,v]  = length(which(data$dist_both  == values[v] & data$exit_status2 == 1))/length(which(data$dist_both  == values[v]))
  }
  
  limy = c(0, max(hazards, na.rm = T))
  plot(values,rep(NA,length(values)),ylim=limy,ylab="Hazard rate",xlab="Distance to threshold")
  lines(values, hazards[1,], col = colors[1], lwd = 3, lty = 2)
  lines(values, hazards[2,], col =  colors[2], lwd = 3, lty = 2)
  lines(values, hazards[3,], col =  colors[3], lwd = 4)
  legend("bottomright", legend = c("Grade", "Echelon", "Double"),lty = c(2,2,1) , col = colors, lwd = 3)
}  


### II.2 Outputs ####


### II.2.1 TTH1 ####
subdata = data_min
subdata = subdata[which(subdata$left_censored == F & subdata$c_cir_2011 == "TTH1"),]
hazard_by_duree(data = subdata)
hazard_by_ech(data = subdata)
hazard_by_distance(data = subdata)

pdf(paste0(fig_path,"hazard_by_duree_TTH1.pdf"))
hazard_by_duree(data = subdata)
abline(v = 3, lwd = 3)
abline(v = 10, lwd = 3)
dev.off()

pdf(paste0(fig_path,"hazard_by_ech_TTH1.pdf"))
hazard_by_ech(data = subdata)
abline(v = 4, lwd = 3)
abline(v = 7, lwd = 3)
dev.off()

# Variantes durée aff
subdata2 = subdata
subdata2$time = subdata2$annee - subdata2$an_aff +1
pdf(paste0(fig_path,"hazard_by_duree_TTH1_bis.pdf"))
hazard_by_duree(data = subdata2)
abline(v = 3, lwd = 3)
abline(v = 10, lwd = 3)
dev.off()


### II.2.2 TTH2 ####

subdata = data_min
subdata = subdata[which(subdata$left_censored == F & subdata$c_cir_2011 == "TTH2"),]
hazard_by_duree(data = subdata)
hazard_by_ech(data = subdata)
hazard_by_distance(data = subdata)

pdf(paste0(fig_path,"hazard_by_duree_TTH2.pdf"))
hazard_by_duree(data = subdata)
abline(v = 6, lwd = 3)
dev.off()

pdf(paste0(fig_path,"hazard_by_ech_TTH2.pdf"))
hazard_by_ech(data = subdata)
abline(v = 5, lwd = 3)
dev.off()

# Variantes durée aff
subdata2 = subdata
subdata2$time = subdata2$annee - subdata2$an_aff +1
pdf(paste0(fig_path,"hazard_by_duree_TTH2_bis.pdf"))
hazard_by_duree(data = subdata2, corps = T)
abline(v = 6, lwd = 3)
dev.off()
pdf(paste0(fig_path,"hazard_by_dist_TTH2_bis.pdf"))
hazard_by_distance(data = subdata2)
abline(v = 0, lwd = 3)
dev.off()




### II.2.2 TTH3 ####


subdata = data_min
subdata = subdata[which(subdata$left_censored == F & subdata$c_cir_2011 == "TTH3"),]
hazard_by_duree(data = subdata)
hazard_by_ech(data = subdata)
hazard_by_distance(data = subdata)

pdf(paste0(fig_path,"hazard_by_duree_TTH3.pdf"))
hazard_by_duree(data = subdata)
abline(v = 5, lwd = 3)
dev.off()

pdf(paste0(fig_path,"hazard_by_ech_TTH3.pdf"))
hazard_by_ech(data = subdata)
abline(v = 6, lwd = 3)
dev.off()

pdf(paste0(fig_path,"hazard_by_dist_TTH3.pdf"))
hazard_by_distance(data = subdata)
abline(v = 0)
dev.off()


### II.2.2 TTH4 ####

subdata = data_min
subdata = subdata[which(subdata$left_censored == F & subdata$c_cir_2011 == "TTH4"),]
hazard_by_duree(data = subdata)
hazard_by_ech(data = subdata)
hazard_by_distance(data = subdata)

pdf(paste0(fig_path,"hazard_by_duree_TTH4.pdf"))
hazard_by_duree(data = subdata)
dev.off()

pdf(paste0(fig_path,"hazard_by_ech_TTH4.pdf"))
hazard_by_ech(data = subdata)
dev.off()


### II.2.5 All ####


