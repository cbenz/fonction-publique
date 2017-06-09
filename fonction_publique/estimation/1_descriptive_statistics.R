




######## Descriptive statistics ########




######## I. Descriptive statistics ########

## I.1 Sample description ####


## I.2 Censoring ####

data_id$right = as.numeric(data_id$right_censored)
data_id$left = as.numeric(data_id$left_censored)

mean_right <- aggregate(data_id$right, by = list(data_id$c_cir_2011), FUN=mean)    
mean_left  <- aggregate(data_id$left,  by = list(data_id$c_cir_2011), FUN=mean)    

# Censoring by time spent in 2011 
mean_right_by_time <- aggregate(data_id$right, by = list(data_id$annee_min_entree_dans_grade), FUN=mean)    

# Censoring by echelon
mean_right_by_ech <- aggregate(data_id$right, by = list(data_id$echelon_2011), FUN=mean)    


## I.3 Survival and hazard ####

### I.3.1 Survival by grade ####

hazard_by_duree = function(data, save = F, sample)
{
  grade = seq(1, max(data$time))
  hazard = numeric(length(grade))
  for (g in 1:length(grade))
  {
    hazard[g] =   length(which(data$time ==  grade[g] & data$exit_status2 == 1))/length(which(data$time == grade[g]))
  }  
  plot(grade, hazard)
  title(paste0("hazard rate by duration in grade ", sample))
}  

hazard_by_duree(data = data_min[which(data_min$c_cir_2011 == "TTH1" & data_min$left_censored == F),],  sample = "TTH1")
hazard_by_duree(data = data_max[which(data_max$c_cir_2011 == "TTH1" & data_max$left_censored == F),],  sample = "TTH1")

hazard_by_duree(data = data_min[which(data_min$c_cir_2011 == "TTH2" & data_min$left_censored == F),],  sample = "TTH2")
hazard_by_duree(data = data_max[which(data_max$c_cir_2011 == "TTH2" & data_max$left_censored == F),],  sample = "TTH2")

hazard_by_duree(data = data_min[which(data_min$c_cir_2011 == "TTH3" & data_min$left_censored == F),],  sample = "TTH3")
hazard_by_duree(data = data_max[which(data_max$c_cir_2011 == "TTH3" & data_max$left_censored == F),],  sample = "TTH3")

hazard_by_duree(data = data_min[which(data_min$c_cir_2011 == "TTH4" & data_min$left_censored == F),],  sample = "TTH4")
hazard_by_duree(data = data_max[which(data_max$c_cir_2011 == "TTH4" & data_max$left_censored == F),],  sample = "TTH4")


### I.3.2 Survival by echelon ####

hazard_by_ech = function(data, save = F, sample)
{
  ech = 1:12
  hazard = numeric(length(ech))
  for (e in 1:length(ech))
  {
    hazard[e] =   length(which(data$echelon == ech[e] & data$exit_status2 == 1))/length(which(data$echelon == ech[e]))
  }  
  plot(ech, hazard)
  title(paste0("Hazard rate by echelon ", sample))
}  

hazard_by_ech(data = data_max,  sample = "All")
hazard_by_ech(data = data_max[which(data_max$c_cir_2011 == "TTH1"& data_max$left_censored == F),],  sample = "TTH1")
hazard_by_ech(data = data_max[which(data_max$c_cir_2011 == "TTH2"& data_max$left_censored == F),],  sample = "TTH2")
hazard_by_ech(data = data_max[which(data_max$c_cir_2011 == "TTH3"& data_max$left_censored == F),],  sample = "TTH3")
hazard_by_ech(data = data_max[which(data_max$c_cir_2011 == "TTH4"& data_max$left_censored == F),],  sample = "TTH4")

hazard_by_ech(data = data_min,  sample = "All")
hazard_by_ech(data = data_min[which(data_min$c_cir_2011 == "TTH1"& data_min$left_censored == F),],  sample = "TTH1")
hazard_by_ech(data = data_min[which(data_min$c_cir_2011 == "TTH2"& data_min$left_censored == F),],  sample = "TTH2")
hazard_by_ech(data = data_min[which(data_min$c_cir_2011 == "TTH3"& data_min$left_censored == F),],  sample = "TTH3")
hazard_by_ech(data = data_min[which(data_min$c_cir_2011 == "TTH4"& data_min$left_censored == F),],  sample = "TTH4")


## I.3.3 Distance to threshold ####


hazard_by_distance = function(data, save = F, type = "choix", colors = c("blue", "red", "darkgreen"), title = "")
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
  
  
  plot(values,rep(NA,length(values)),ylim=c(0,1),ylab="Hazard rate",xlab="Distance to threshold")
  lines(values, hazards[1,], col = colors[1], lwd = 3)
  lines(values, hazards[2,], col =  colors[2], lwd = 3)
  lines(values, hazards[3,], col =  colors[3], lwd = 3)
  legend("topleft", legend = (c("Grade", "Echelon", "Both")), col = colors, lty = 1, lwd = 3)
  title(paste0("Hazard rate distance to thresholds", title))
  
}  

subdata = data_min
hazard_by_distance(data = subdata[which(subdata$left_censored == F & subdata$echelon != -1),])
hazard_by_distance(data = subdata[which(subdata$left_censored == F & subdata$echelon != -1 & subdata$c_cir_2011 == "TTH1"),])
hazard_by_distance(data = subdata[which(subdata$left_censored == F & subdata$echelon != -1 & subdata$c_cir_2011 == "TTH2"),])
hazard_by_distance(data = subdata[which(subdata$left_censored == F & subdata$echelon != -1 & subdata$c_cir_2011 == "TTH3"),])


# Variantes durée pour tth1 et tth2
subdata2 = subdata
obs_grade = which(subdata2$c_cir_2011 == "TTH1" | subdata2$c_cir_2011 == "TTH2")
subdata2$time[obs_grade] = subdata2$annee[obs_grade]  - subdata2$an_aff[obs_grade] +1
hazard_by_distance(data = subdata2[which(subdata2$left_censored == F & subdata2$echelon != -1 & subdata2$c_cir_2011 == "TTH1"),])


hazard_by_distance(data = subdata[which(subdata$left_censored == F & subdata$echelon != -1 & subdata$c_cir_2011 == "TTH2"),], title = " TTH2\n (duree dans le grade)")
hazard_by_distance(data = subdata2[which(subdata2$left_censored == F & subdata2$echelon != -1 & subdata2$c_cir_2011 == "TTH2"),], title = " TTH2\n (duree dans le corps)")



## I.4 KM estimation ####

subdata = data_id[which(data_id$left_censored == F),]
subdata$time = subdata$duree_min

# All
surv_all <- Surv(subdata$time, subdata$observed)
fit_all <- survfit(surv_all ~ 1)
plot(fit_all, main="Overall survival function \n (Kaplan-Meier estimates)",
     xlab="time", ylab="Survival probability")

# By grade
surv1  = survfit(Surv(time, observed) ~ c_cir_2011, data = subdata) 
plot(surv1, main="Overall survival function \n (Kaplan-Meier estimates)",
     xlab="time", ylab="Survival probability",
     lty = c(1,2,2,1), col = c("black", "grey50","black", "grey50"), lwd = 3)
legend("topright", ncol = 2, legend = c("TTH1", "TTH2", "TTH3", "TTH4"), col = c("black", "grey50","black", "grey50"),  lty = c(1,2,2,1), lwd = 3)



