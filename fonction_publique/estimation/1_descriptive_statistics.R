




######## Descriptive statistics ########

##  Loading data ####


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
fig_path = paste0(git_path,"ecrits/Points AB/")
tab_path = paste0(git_path,"ecrits/modelisation_carriere/Tables/")

# Chargement de la base
filename = paste0(data_path,"clean_data_finalisation/data_ATT_2002_2015.csv")
#filename = paste0(data_path,"clean_data_finalisation/data_ATT_2002_2015_redef_var.csv")
data_long = read.csv(filename)


## 0.2 Work on data ####

## Corrections (to move to .py)
data_long$echelon[which(data_long$echelon == 55555)] = 12

# Exit_status
data_long$annee_exit = ave(data_long$annee, data_long$ident, FUN = max) 
data_long$exit_status2 = ifelse(data_long$annee == data_long$annee_exit,1, 0)
data_long$exit_status2[data_long$right_censored] = 0

# Format bolean                     
to_bolean = c("indicat_ch_grade", "ambiguite", "right_censored", "left_censored", "exit_status")
data_long[, to_bolean] <- sapply(data_long[, to_bolean], as.logical)

# Variables creation
data_long$observed  = ifelse(data_long$right_censored == 1, 0, 1) 
data_long$echelon_2011 = ave(data_long$echelon*(data_long$annee == 2011), data_long$ident, FUN = max)
data_long$time_spent_in_grade_max  = data_long$annee - data_long$annee_min_entree_dans_grade + 1
data_long$time_spent_in_grade_min  = data_long$annee - data_long$annee_max_entree_dans_grade + 1


## Institutional parameters (question: default value?)
# Grade duration
data_long$D_exam = 20
data_long$D_exam[which(data_long$c_cir_2011 == "TTH1")] = 3
data_long$D_choice = 20
data_long$D_choice[which(data_long$c_cir_2011 == "TTH1")] = 10
data_long$D_choice[which(data_long$c_cir_2011 == "TTH2")] = 6
data_long$D_choice[which(data_long$c_cir_2011 == "TTH3")] = 5

# Echelon (default = ?)
data_long$E_exam = 12
data_long$E_exam[which(data_long$c_cir_2011 == "TTH1")] = 4
data_long$E_choice = 12
data_long$E_choice[which(data_long$c_cir_2011 == "TTH1")] = 7
data_long$E_choice[which(data_long$c_cir_2011 == "TTH2")] = 5
data_long$E_choice[which(data_long$c_cir_2011 == "TTH3")] = 6


## 0.3 data for estimations ####

# One line per year of observation (min and max)

# One line per year of observation (min and max)
data_min = data_long[which(data_long$annee >= data_long$annee_min_entree_dans_grade),]
data_min$time = data_min$time_spent_in_grade_max 
data_max = data_long[which(data_long$annee >= data_long$annee_max_entree_dans_grade),]
data_max$time = data_max$time_spent_in_grade_min

## Corrections (to move to .py)
pb_ech = unique(data_max$ident[which(data_max$echelon == -1)])
data_max = data_max[-which(is.element(data_max$ident, pb_ech)),]
data_min = data_min[-which(is.element(data_min$ident, pb_ech)),]

# One line per ident data
data_id = data_long[!duplicated(data_long$ident),]


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



# pdf(paste0(fig_path,"KM.pdf"))
# par(mar=c(3,3,1,1))
# layout(matrix(c(1, 2, 3, 4), nrow=2,ncol=2, byrow=TRUE), heights=c(3, 3))
# my.surv <- Surv(data_id$time_max[data_id$c_cir == "TTH1"], data_id$observed[data_id$c_cir == "TTH1"])
# my.fit <- survfit(my.surv ~ 1)
# plot(my.fit, main="KM for TTH1",
#      xlab="time", ylab="survival function")
#dev.off()
