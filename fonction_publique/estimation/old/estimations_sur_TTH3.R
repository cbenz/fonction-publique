




######## 0. Initialisation ########

rm(list = ls()); gc()

# Packages
#install.packages("OIsurv");install.packages("rms");install.packages("emuR");install.packages("RColorBrewer");install.packages("RcmdrPlugin");install.packages("flexsurv")
library(OIsurv)
library(rms)
library(emuR)
library(RColorBrewer)
library(RcmdrPlugin.survival)
library(flexsurv)


## 0.1 Loading data ####

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

data_long = data_long[which(data_long$c_cir_2011 == "TTH3"),]

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



### I.2.1 Survival by grade ####


hazard_by_duree = function(data, save = F, sample, time = 'time_spent_in_grade_max')
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

hazard_by_duree(data = data_max[which(data_max$c_cir_2011 == "TTH3" & data_max$left_censored == F),],  sample = "TTH3")
hazard_by_duree(data = data_min[which(data_min$c_cir_2011 == "TTH3" & data_min$left_censored == F),],  sample = "TTH3")


### I.2.2 Survival by echelon ####

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

hazard_by_ech(data = data_max[which(data_max$c_cir_2011 == "TTH3" & data_max$left_censored == F),],  sample = "TTH3")
hazard_by_ech(data = data_min[which(data_min$c_cir_2011 == "TTH3" & data_min$left_censored == F),],  sample = "TTH3")



## I.2.3 KM estimation ####

subdata = data_id[which(data_id$left_censored == F),]
subdata$time = subdata$duree_min

# All
surv_all <- Surv(subdata$time, subdata$observed)
fit_all <- survfit(surv_all ~ 1)
plot(fit_all, main="Overall survival function \n (Kaplan-Meier estimates)",
     xlab="time", ylab="Survival probability")

######## II. Estimations ########

## II.1 Parametric estimation ####


plot_comp_fit_param = function(data, save = F, grade = "all")
{
  if (!is.element(grade, c("all","TTH1","TTH2","TTH3","TTH4"))){print("Not a grade"); return()}
  if (grade != "all"){data = data[which(data$c_cir_2011 == grade),]}
  
  
  srFit_exp <- flexsurvreg(Surv(duree_min, observed) ~ sexe + generation_group, data = data, dist = "exponential")
  srFit_loglog <- flexsurvreg(Surv(duree_min, observed) ~ sexe + generation_group, data = data, dist = "llogis")
  srFit_gamma <- flexsurvreg(Surv(duree_min, observed) ~ sexe + generation_group, data = data,  dist = "gengamma")
  srFit_weibull <- flexsurvreg(Surv(duree_min, observed) ~ sexe + generation_group, data = data,  dist = "weibull")
  srFit_gomp <- flexsurvreg(Surv(duree_min, observed) ~ sexe + generation_group, data = data,  dist = "gompertz")
  
  colors = rainbow(5)
  plot(srFit_exp, col = c(colors[1]), xlab = "Duration in grade", ylab = "Survival functions")
  lines(srFit_loglog, col = c(colors[2]))
  lines(srFit_gamma, col = c(colors[3]))
  lines(srFit_weibull, col = c(colors[4]))
  lines(srFit_gomp, col = c(colors[5]))
  title(grade)
  legend("bottomleft", legend = c("KM", "Exp", "Loglog", "Gen. gamma", "Weibull", "Gompertz"), col = c("black",colors), lty = 1)
}  

plot_comp_fit_param(data_id, grade = "TTH3")


## II.3  Cox PH with time-dependent variables ####

## II.3.1  0/1 Treatment ####

data = data_max[which(data_max$left_censored == F & data_max$c_cir_2011 == "TTH3"),]
data = data_max[which(data_max$left_censored == F),]
data = data_min[which(data_max$left_censored == F),]

# Start/stop
data$start = data$time - 1
data$stop = data$time 

# Distance variables
data$I_echelon = ifelse(data$echelon >= data$E_choice, 1, 0) 
data$I_grade = ifelse(data$time >= data$D_choice, 1, 0) 
data$I_both = ifelse(data$time >= data$D_choice & data$echelon >= data$E_choice, 1, 0) 

coxph.fit1 = coxph(Surv(start, stop, exit_status2) ~  sexe + factor(generation_group) +  I_echelon,
                   data=data)
coxph.fit2 = coxph(Surv(start, stop, exit_status2) ~  sexe + factor(generation_group) +  I_both,
                   data=data)

##### II.3.2  Distance to threshold dummies (Chetty) #######

# Start/stop
data$start = data$time - 1
data$stop = data$time 

# Distance variables
data$dist_echelon = data$echelon - data$E_choice 
data$dist_grade = data$time - data$D_choice 

for(d in unique(data$dist_echelon)) {
  if (d<=-4){data[paste("dist_echelon_m4",sep="")] <- ifelse(data$dist_echelon<=-4,1,0)}
  else if  (d>=4){data[paste("dist_echelon_p4",sep="")] <- ifelse(data$dist_echelon>=4,1,0)}
  else if  (d<0){data[paste("dist_echelon_m",abs(d),sep="")] <- ifelse(data$dist_echelon==d,1,0)}
  else if  (d==0){data[paste("dist_echelon_",d,sep="")] <- ifelse(data$dist_echelon==d,1,0)}
  else if  (d>0){data[paste("dist_echelon_p",d,sep="")] <- ifelse(data$dist_echelon==d,1,0)}
}

coxph.fit1 = coxph(Surv(start, stop, exit_status2) ~  sexe + generation_group + 
                     dist_echelon_m3 + dist_echelon_m2 + dist_echelon_m1 + dist_echelon_0 + 
                     dist_echelon_p1 + dist_echelon_p2 + dist_echelon_p3 + dist_echelon_p4,
                   data=data)



##### Check weird #####

table(data_max$echelon[data_max$exit_status2 == 1])
table(data_max$duree_max[data_max$exit_status2 == 1])


## Interacting conditions
data1 = data_min
data1 = data1[which(data1$left_censored == F & data1$echelon != -1),]
data1$dist_grade =  data1$time  - data1$D_choice 
data1$dist_echelon = data1$echelon - data1$E_choice 
data1$dist_both = pmin(data1$dist_grade, data1$dist_echelon)

values = (min(min(data1$dist_grade), min(data1$dist_echelon), min(data1$dist_both)):
                 min(max(data1$dist_grade), max(data1$dist_echelon), max(data1$dist_both)))
hazards = matrix(ncol = length(values), nrow = 3)

for (v in 1:length(values))
{
hazards[1,v]  = length(which(data1$dist_grade  == values[v] & data1$exit_status2 == 1))/length(which(data1$dist_grade  == values[v]))
hazards[2,v]  = length(which(data1$dist_echelon  == values[v] & data1$exit_status2 == 1))/length(which(data1$dist_echelon  == values[v]))
hazards[3,v]  = length(which(data1$dist_both  == values[v] & data1$exit_status2 == 1))/length(which(data1$dist_both  == values[v]))
}

colors = c("blue", "red", "darkgreen")

plot(values,rep(NA,length(values)),ylim=c(0,1),ylab="Hazard rate",xlab="Distance to threshold")
lines(values, hazards[1,], col = colors[1], lwd = 3)
lines(values, hazards[2,], col =  colors[2], lwd = 3)
lines(values, hazards[3,], col =  colors[3], lwd = 3)
legend("topleft", legend = (c("Grade", "Echelon", "Both")), col = colors, lty = 1, lwd = 3)

title(paste0("Hazard rate by echelon ", sample))



