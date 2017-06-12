




######## Descriptive statistics ########


source(paste0(wd, "0_work_on_data.R"))
datasets = load_and_clean(data_path, "data_ATT_2002_2015_2.csv")
data_id = datasets[[1]]
data_max = datasets[[2]]
data_min = datasets[[3]]



## I. Sample description ####




## I.2 Censoring ####

data_id$right = as.numeric(data_id$right_censored)
data_id$left = as.numeric(data_id$left_censored)

mean_right <- aggregate(data_id$right, by = list(data_id$c_cir_2011), FUN=mean)    
mean_left  <- aggregate(data_id$left,  by = list(data_id$c_cir_2011), FUN=mean)    

# Censoring by time spent in 2011 
mean_right_by_time <- aggregate(data_id$right, by = list(data_id$annee_min_entree_dans_grade), FUN=mean)    

# Censoring by echelon
mean_right_by_ech <- aggregate(data_id$right, by = list(data_id$echelon_2011), FUN=mean)    



## II. Graphical evidence on exit grade ####

### II.1 Functions ####

# Hazard by duration in grade
hazard_by_duree = function(data, save = F)
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
  plot(grade, hazard, type ="l", lwd = 3, xlab = "Duration in grade", ylab = "Hazard rate", col = "darkcyan")
  par(new = T)
  plot(grade, effectif, type ="l", lty = 2, lwd = 2, , axes=F, xlab=NA, ylab=NA)
  axis(side = 4)
  mtext(side = 4, line = 3, 'Effectifs')
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
  plot(ech, effectif, type ="l", lty = 2, lwd = 2, , axes=F, xlab=NA, ylab=NA)
  axis(side = 4)
  mtext(side = 4, line = 3, 'Effectifs')
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
abline(v = 3)
abline(v = 10)
dev.off()

pdf(paste0(fig_path,"hazard_by_ech_TTH1.pdf"))
hazard_by_ech(data = subdata)
abline(v = 4)
abline(v = 7)
dev.off()

# Variantes durée aff
subdata2 = subdata
subdata2$time = subdata2$annee - subdata2$an_aff +1
pdf(paste0(fig_path,"hazard_by_duree_TTH1_bis.pdf"))
hazard_by_duree(data = subdata2)
abline(v = 3)
abline(v = 10)
dev.off()


### II.2.2 TTH2 ####

subdata = data_min
subdata = subdata[which(subdata$left_censored == F & subdata$c_cir_2011 == "TTH2"),]
hazard_by_duree(data = subdata)
hazard_by_ech(data = subdata)
hazard_by_distance(data = subdata)

pdf(paste0(fig_path,"hazard_by_duree_TTH2.pdf"))
hazard_by_duree(data = subdata)
abline(v = 6)
dev.off()

pdf(paste0(fig_path,"hazard_by_ech_TTH2.pdf"))
hazard_by_ech(data = subdata)
abline(v = 5)
dev.off()

# Variantes durée aff
subdata2 = subdata
subdata2$time = subdata2$annee - subdata2$an_aff +1
pdf(paste0(fig_path,"hazard_by_duree_TTH2_bis.pdf"))
hazard_by_duree(data = subdata2)
abline(v = 6)
dev.off()
pdf(paste0(fig_path,"hazard_by_dist_TTH2_bis.pdf"))
hazard_by_distance(data = subdata2)
abline(v = 0)
dev.off()




### II.2.2 TTH3 ####


subdata = data_min
subdata = subdata[which(subdata$left_censored == F & subdata$c_cir_2011 == "TTH3"),]
hazard_by_duree(data = subdata)
hazard_by_ech(data = subdata)
hazard_by_distance(data = subdata)

pdf(paste0(fig_path,"hazard_by_duree_TTH3.pdf"))
hazard_by_duree(data = subdata)
abline(v = 5)
dev.off()

pdf(paste0(fig_path,"hazard_by_ech_TTH3.pdf"))
hazard_by_ech(data = subdata)
abline(v = 6)
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
abline(v = 5)
dev.off()

pdf(paste0(fig_path,"hazard_by_ech_TTH4.pdf"))
hazard_by_ech(data = subdata)
abline(v = 6)
dev.off()


### II.2.5 All ####


