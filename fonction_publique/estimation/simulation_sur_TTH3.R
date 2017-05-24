

#### 0. Initialisation ####

rm(list = ls()); gc()

# path
place = "ippS"
if (place == "ippS"){
  data_path = "M:/CNRACL/output/base_AT_clean_2007_2011/"
  git_path =  'U:/Projets/CNRACL/fonction-publique/fonction_publique/'
}
if (place == "ippL"){
  data_path = "M:/CNRACL/output/base_AT_clean_2007_2011/"
  git_path =  'C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/'
}
if (place == "mac"){
  data_path = "/Users/simonrabate/Desktop/data/CNRACL/output/"
  git_path =  '/Users/simonrabate/Desktop/IPP/CNRACL/fonction_publique/'
}

# Packages
#install.packages("OIsurv");install.packages("rms");install.packages("emuR");install.packages("RColorBrewer");install.packages("RcmdrPlugin");install.packages("pec")
#install.packages("prodlim")
library(OIsurv)
library(rms)
library(emuR)
library(RColorBrewer)
library(RcmdrPlugin.survival)

# Chargement de la base
filename = paste0(data_path,"base_AT_clean.csv")
data_long = read.csv(filename) 

# MODIF A DEPLACER: cleaning when right censoring and not duration in grade = 5
data_long = data_long[-which(data_long$duration_in_grade_from_2011 < 5 & data_long$right_censoring== 'True'),]

data_long$generation_group = 9
data_long$generation_group[data_long$generation<1990] = 8
data_long$generation_group[data_long$generation<1985] = 7
data_long$generation_group[data_long$generation<1980] = 6
data_long$generation_group[data_long$generation<1975] = 5
data_long$generation_group[data_long$generation<1970] = 4
data_long$generation_group[data_long$generation<1965] = 3

data_long$ind_exit_once = ave(data_long$exit_status, data_long$ident, FUN = max) 
data_long$observed = ifelse(data_long$ind_exit_once == 1, 1, 0)
data_long$time_min = data_long$min_duration_in_grade + data_long$duration_in_grade_from_2011
data_long$time_max = data_long$max_duration_in_grade + data_long$duration_in_grade_from_2011


# Mise au format data 1obs/indiv
data_id = data_long[,c("ident", "c_cir", "generation_group","max_duration_in_grade","min_duration_in_grade","duration_in_grade_from_2011", 
                       "observed",  "right_censoring", "time_min", "time_max")]
data_id = data_id[!duplicated(data_id$ident),]

## Data grade TTH3 
data_TTH3 <- data_id[data_id$c_cir == 'TTH3',]
data_TTH3 <- data_TTH3[-which(data_TTH3$generation_group == '9'),]

## Learning and prediction sample
list_id = data_TTH3$ident
list_learning = sample(list_id, ceiling(length(list_id)/2))
list_test = setdiff(list_id, list_learning)
data_learning = data_id[which(is.element(data_id$ident, list_learning)),]
data_test     = data_id[which(is.element(data_id$ident, list_test)),]

length(which(data_TTH3$right_censoring == 'True'))/length(data_TTH3$right_censoring)

## I. Estimation ####

## KM
srFit_KM <- survfit(Surv(data_learning$time_max, data_learning$observed) ~ 1)
summary(srFit_KM)

## Exponential
srFit_exp <- survreg(Surv(time_max, observed) ~  1 + factor(generation_group), data = data_learning, dist = "exponential")
summary(srFit_exp)

## Weibull 
srFit_weibull <- survreg(Surv(time_max, observed) ~  1 + factor(generation_group), data = data_learning, dist = "weibull")
summary(srFit_weibull)


### II. Simulation ###

attach(data_test)
tirage<-function(var)
{
  t<-rbinom(1,1,var) # Loi binomiale 
  return(t)
}
### Predicted exit date
duration = max_duration_in_grade
predicted_exit_exp = rep(NA,length(ident))
data_sim_exp <- data_test
predicted_exit_wei = rep(NA,length(ident))
data_sim_wei <- data_test 

for (y in seq(2011, 2015, 1))
{
  # Keep only individuals that are not left
  list_wei = which(is.na(predicted_exit_wei))
  data_sim_wei = data_test[list_wei,]
  list_exp = which(is.na(predicted_exit_exp))
  data_sim_exp = data_test[list_exp,]  
  # Computing hazard rate bw y an y+1  
  intercept.wei = predict(srFit_weibull, newdata = data_sim_wei,type="linear")
  intercept.exp = predict(srFit_exp, newdata = data_sim_exp,type="linear")  
  t = duration[list_wei] + 1  # Hyp: proba of exit at t+0.5
  scale = srFit_weibull$scale
  hazard_wei <-dweibull(t, scale=exp(intercept.wei), shape=1/scale)/pweibull(t, scale=exp(intercept.wei), shape=1/scale, lower.tail=FALSE)
  hazard_exp <-dweibull(1, scale=exp(intercept.exp), shape=1)/pweibull(1, scale=exp(intercept.exp), shape=1, lower.tail=FALSE)
#  print(c(y, "mean wei", mean(hazard_wei), "mean exp", mean(hazard_exp)))
  # Drawing exit based on the predicted probability
  exit_wei = as.numeric(lapply(hazard_wei, tirage))
  exit_exp = as.numeric(lapply(hazard_exp, tirage))
  # Saving exit date when predicted
  predicted_exit_wei[list_wei] = ifelse(exit_wei == 1, y+1, NA)
  predicted_exit_exp[list_exp] = ifelse(exit_exp == 1, y+1, NA)
  # Incrementing duration 
  duration = duration + 1 
}
detach(data_test)


# Observed/predicted survival between 2011 and 2015
observed_exit = data_test$duration_in_grade_from_2011 + 2011
observed_exit[data_test$right_censoring == "True"] = NA  
annee <- seq(2011, 2015, 1)
survival = matrix(ncol = length(annee), nrow = 3)
hazard_rate = matrix(ncol = length(annee), nrow = 3)

observed_exit[is.na(observed_exit)] = 9999
predicted_exit_wei[is.na(predicted_exit_wei)] = 9999
predicted_exit_exp[is.na(predicted_exit_exp)] = 9999

for (y in (1:length(annee)))
{
  n = length(observed_exit)
  # Survival Rate
  survival[1, y] = length(which(observed_exit > annee[y] | is.na(observed_exit)))/n
  survival[2, y] = length(which(predicted_exit_wei > annee[y] | is.na(predicted_exit_wei)))/n
  survival[3, y] = length(which(predicted_exit_exp > annee[y] | is.na(predicted_exit_exp)))/n
  # Hazard Rate
  if (y < length(annee))
  {
  hazard_rate[1, y] = length(which(observed_exit == annee[y]+1))/length(which(observed_exit >= annee[y]))
  hazard_rate[2, y] = length(which(predicted_exit_wei == annee[y]+1))/length(which(predicted_exit_wei >= annee[y]))
  hazard_rate[3, y] = length(which(predicted_exit_exp == annee[y]+1))/length(which(predicted_exit_exp >= annee[y]))
  }
}  


# Plot
plot(annee, rep(NA, length(annee)), ylim = c(0,1),  ylab = "Survival rate",xlab = "Year")
lines(annee, survival[1, ], col="grey20", lwd=3)
lines(annee, survival[2, ], col="grey50", lwd=3)
lines(annee, survival[3, ], col="grey80", lwd=3)
legend("bottomleft", legend = c("Observed", "Weibull","Exponential"), 
       lty = 1, col = c("grey20", "grey50", "grey80"), lwd = 3)

# Plot
plot(annee, rep(NA, length(annee)), ylim = c(0,0.4),  ylab = "Hazard rate",xlab = "Year")
lines(annee, hazard_rate[1, ], col="grey20", lwd=3)
lines(annee, hazard_rate[2, ], col="grey50", lwd=3)
lines(annee, hazard_rate[3, ], col="grey80", lwd=3)
legend("topleft", legend = c("Observed", "Weibull","Exponential"), 
       lty = 1, col = c("grey20", "grey50", "grey80"), lwd = 3)
  

#### Test effect of censoring on estimation
data_TTH3 <- data_id[data_id$c_cir == 'TTH3',]
data_TTH3 <- data_TTH3[-which(data_TTH3$generation_group == '9'),]

data_TTH3$duration_censored1 = pmin(data_TTH3$duration_in_grade_from_2011, 4)
data_TTH3$duration_censored2 = pmin(data_TTH3$duration_in_grade_from_2011, 3)
data_TTH3$observed1 = ifelse(data_TTH3$duration_censored1<4,1,0)
data_TTH3$observed2 = ifelse(data_TTH3$duration_censored2<3,1,0)
data_TTH3$time_max1 = data_TTH3$duration_censored1 + data_TTH3$max_duration_in_grade
data_TTH3$time_max2 = data_TTH3$duration_censored2 + data_TTH3$max_duration_in_grade

table(data_TTH3$duration_in_grade_from_2011, data_TTH3$observed)
table(data_TTH3$duration_censored1, data_TTH3$observed1)
table(data_TTH3$duration_censored2, data_TTH3$observed2)

list_id = data_TTH3$ident
list_learning = sample(list_id, ceiling(length(list_id)/2))
list_test = setdiff(list_id, list_learning)
data_learning = data_TTH3[which(is.element(data_TTH3$ident, list_learning)),]
data_test     = data_TTH3[which(is.element(data_TTH3$ident, list_test)),]

## Weibull 
srFit_weibull <- survreg(Surv(time_max, observed) ~  1 + factor(generation_group), data = data_learning, dist = "weibull")
summary(srFit_weibull)
## Weibull 
srFit_weibull1 <- survreg(Surv(time_max1, observed1) ~  1 + factor(generation_group), data = data_learning, dist = "weibull")
summary(srFit_weibull1)
## Weibull 
srFit_weibull2 <- survreg(Surv(time_max2, observed2) ~  1 + factor(generation_group), data = data_learning, dist = "weibull")
summary(srFit_weibull2)


# Hazards rate in 2011
# Keep only individuals that are not left
# Computing hazard rate bw y an y+1  
intercept.wei = predict(srFit_weibull, newdata = data_test,type="linear")
intercept.wei1 = predict(srFit_weibull1, newdata = data_test,type="linear")
intercept.wei2 = predict(srFit_weibull2, newdata = data_test,type="linear")

t = data_test$max_duration_in_grade + 0.5  # Hyp: proba of exit at t+0.5
scale = srFit_weibull$scale
scale1 = srFit_weibull1$scale
scale2 = srFit_weibull2$scale
hazard_wei <-dweibull(t, scale=exp(intercept.wei), shape=1/scale)/pweibull(t, scale=exp(intercept.wei), shape=1/scale, lower.tail=FALSE)
hazard_wei1 <-dweibull(t, scale=exp(intercept.wei1), shape=1/scale1)/pweibull(t, scale=exp(intercept.wei1), shape=1/scale1, lower.tail=FALSE)
hazard_wei2 <-dweibull(t, scale=exp(intercept.wei2), shape=1/scale1)/pweibull(t, scale=exp(intercept.wei2), shape=1/scale2, lower.tail=FALSE)

print(c("mean wei", mean(hazard_wei), 
        "mean wei1", mean(hazard_wei1),
        "mean wei2", mean(hazard_wei2)))
  
  