

#### 0. Initialisation ####

rm(list = ls()); gc()

# path
place = "mac"
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
fig_path = paste0(git_path,"ecrits/Points AB/")
tab_path = paste0(git_path,"ecrits/modelisation_carriere/Tables/")


# Packages
#install.packages("OIsurv");install.packages("rms");install.packages("emuR");install.packages("RColorBrewer");install.packages("RcmdrPlugin");install.packages("pec")
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
data_learning = data_TTH3[which(is.element(data_TTH3$ident, list_learning)),]
data_test     = data_TTH3[which(!is.element(data_TTH3$ident, list_learning)),]


## I. Estimation ####

## KM
srFit_KM <-survfit(Surv(time_max, observed)~1, data = data_learning)
summary(srFit_KM)

## Exponential
srFit_exp <- survreg(Surv(time_max, observed) ~  1 + as.factor(generation_group) , data = data_learning, dist = "exponential")
summary(srFit_exp)

## Loglogistic
srFit_loglog <- survreg(Surv(time_max, observed) ~  as.factor(generation_group) , data = data_learning,, dist = "loglogistic")
summary(srFit_loglog)

## Gaussian
srFit_gaus <- survreg(Surv(time_max, observed) ~  as.factor(generation_group) , data = data_learning,  dist = "gaussian")
summary(srFit_gauss)

## Weibull 
srFit_weibull <- survreg(Surv(time_max, observed) ~  1 + as.factor(generation_group) , data = data_learning, dist = "weibull")
summary(srFit_weibull)


### II. Fit ###

summary(srFit_weibull)
round(srFit_weibull$coefficients, 3)

# Hazard rate
lambda.wei.i <- exp(-predict(srFit_weibull, data = data_learning, type="linear"))
lambda.wei <- mean(lambda.i, na.rm=TRUE)
lambda.exp.i <- exp(-predict(srFit_exp, data = data_learning, type="linear"))
lambda.exp <- mean(lambda.i, na.rm=TRUE)
t <- seq(0, max(comp$fit$time), len=99)
p <- 1/srFit_weibull$scale
hazard_wei <- lambda * p * (lambda * t)^(p-1)
hazard_exp <- lambda 
plot(t, hazard_wei, type="l", main="Weibull and exponential Hazard rates", 
     xlab="Years in grade", ylab="Hazard Rate")
lines(t, rep(hazard_exp, length(t)))







## II.1 Graphical comparison
#srFit_exp <- survreg(Surv(time_max, observed) ~  1 , data = data_learning, dist = "exponential")
#srFit_weibull <- survreg(Surv(time_max, observed) ~  1 , data = data_learning, dist = "weibull")
comp = list(fit=srFit_KM, lam.e=exp(-coef(srFit_exp)), lam.w=exp(-coef(srFit_weibull)), gam=1/srFit_weibull$scale)

par(mar=c(4,4,1,1))
plot(comp$fit, conf.int=FALSE, las=1, mark.time=FALSE, col='grey60',lwd=3, 
     ylab = "Survival",xlab = "Duration in grade")
tt <- seq(0, max(comp$fit$time), len=99)
lines(tt, pexp(tt, comp$lam.e, low=FALSE), col="grey20", lwd=3)
lines(tt, pweibull(tt, comp$gam, 1/comp$lam.w, low=FALSE), col="black", , lwd=3)
legend("bottomleft", legend = c("KM","Exponential", "Weibull"), lty = 1, col = c("grey60", "grey20", "black"), lwd = 3)


### III. Simulation ###
#srFit_exp <- survreg(Surv(time_max, observed) ~  1 , data = data_learning, dist = "exponential")
#srFit_weibull <- survreg(Surv(time_max, observed) ~  1 , data = data_learning, dist = "weibull")


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

for (y in seq(2011, 2014, 1))
{
# Keep only individuals that are not left
list_wei = which(is.na(predicted_exit_wei))
data_sim_wei = data_sim[list_wei,]
list_exp = which(is.na(predicted_exit_exp))
data_sim_exp = data_sim[list_exp,]  
# Computing hazard rate bw y an y+1  
  lambda.wei <- exp(-predict(srFit_weibull, newdata = data_sim_wei, type="linear"))
  lambda.exp <- exp(-predict(srFit_exp, newdata = data_sim_exp, type="linear"))
  t = duration[list_wei] + 0.5  # Hyp: proba of exit at t+0.5
  p <- 1/srFit_weibull$scale
  hazard_wei <- lambda.wei * p * (lambda.wei * t)^(p-1)  
  hazard_exp <- lambda.exp
# Drawing exit based on the predicted probability
  exit_wei = as.numeric(lapply(hazard_wei, tirage))
  exit_exp = as.numeric(lapply(hazard_exp, tirage))
# Saving exit date when predicted
predicted_exit_wei[list_wei] = ifelse(exit_wei == 1, y+1, NA)
predicted_exit_exp[list_exp] = ifelse(exit_exp == 1, y+1, NA)
# Incrementing duration 
duration = duration + 1 
}

# Observed/predicted survival between 2011 and 2015
observed_exit = duration_in_grade_from_2011 + 2011
observed_exit[right_censoring == "True"] = NA  
annee <- seq(2011, 2015, 1)
survival = matrix(ncol = length(annee), nrow = 3)
for (y in 1:length(annee))
{
n = length(observed_exit)
survival[1, y] = length(which(observed_exit > annee[y] | is.na(observed_exit)))/n
survival[2, y] = length(which(predicted_exit_wei > annee[y] | is.na(predicted_exit_wei)))/n
survival[3, y] = length(which(predicted_exit_exp > annee[y] | is.na(predicted_exit_exp)))/n
}  

# Plot
plot(annee, rep(NA, length(annee)), ylim = c(0,1),  ylab = "Survival rate",xlab = "Year")
lines(annee, survival[1, ], col="grey20", lwd=3)
lines(annee, survival[2, ], col="grey50", lwd=3)
lines(annee, survival[3, ], col="grey80", lwd=3)
legend("bottomleft", legend = c("Observed", "Weibull","Exponential"), 
       lty = 1, col = c("grey20", "grey50", "grey80"), lwd = 3)




# Predicted Exit for the data_test





predict(srFit_weibull)



lfit <- survreg(Surv(time, status) ~ ph.ecog, data=lung)
pct <- 1:98/100   # The 100th percentile of predicted survival is at +infinity
ptime <- predict(lfit, newdata=data.frame(ph.ecog=2), type='quantile',
                 p=pct, se=TRUE)
matplot(cbind(ptime$fit, ptime$fit + 2*ptime$se.fit,
              ptime$fit - 2*ptime$se.fit)/30.5, 1-pct,
        xlab="Months", ylab="Survival", type='l', lty=c(1,2,2), col=1)


data(pbc)
pbc <- pbc[sample(1:NROW(pbc),size=100),]
f1 <- psm(Surv(time,status!=0)~edema+log(bili)+age+sex+albumin,data=pbc)
f2 <- coxph(Surv(time,status!=0)~edema+log(bili)+age+sex+albumin,data=pbc)
f3 <- cph(Surv(time,status!=0)~edema+log(bili)+age+sex+albumin,data=pbc,surv=TRUE)
brier <- pec(list("Weibull"=f1,"CoxPH"=f2,"CPH"=f3),data=pbc,formula=Surv(time,status!=0)~1)
print(brier)
plot(brier)

f1 <- psm(Surv(time_max, observed) ~  sexe +as.factor(generation_group), data=data_learning)
f2 <- coxph(Surv(time_max, observed) ~  sexe +as.factor(generation_group), data=data_learning)

brier <- pec(list("Weibull"=f1, "Exp"=f2), data=data_test, formula=Surv(time_max, observed)  ~1)
print(brier)
plot(brier)





data_prediction = 






