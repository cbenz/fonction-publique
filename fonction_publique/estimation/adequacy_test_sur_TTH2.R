




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
filename = paste0(data_path,"base_AT_clean_2007_2011/base_AT_clean_w_echelon_sex_generation_group.csv")
data_new = read.csv(filename) 
filename = paste0(data_path,"base_AT_clean_2007_2011/base_AT_clean.csv")
data_long = read.csv(filename) 
data_long$generation_group = data_new$generation_group
data_long$sexe = data_new$sexe

data_long$ind_exit_once = ave(data_long$exit_status, data_long$ident, FUN = max) 
data_long$observed = ifelse(data_long$ind_exit_once == 1, 1, 0)
data_long$time_min = data_long$min_duration_in_grade + data_long$duration_in_grade_from_2011
data_long$time_max = data_long$max_duration_in_grade + data_long$duration_in_grade_from_2011


# Mise au format data 1obs/indiv
data_id = data_long[,c("ident", "c_cir","sexe", "generation_group","max_duration_in_grade","min_duration_in_grade","duration_in_grade_from_2011", 
                       "observed",  "right_censoring", "time_min", "time_max")]
data_id = data_id[!duplicated(data_id$ident),]


## Data grade TTH3 
data_TTH3 <- data_id[data_id$c_cir == 'TTH3',]
data_TTH3 <- data_id[-which(data_TTH3$generation_group == '9'),]

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
srFit_exp <- survreg(Surv(time_max, observed) ~ sexe + as.factor(generation_group) , data = data_learning, dist = "exponential")
summary(srFit_exp)

## Loglogistic
srFit_loglog <- survreg(Surv(time_max, observed) ~  sexe +as.factor(generation_group) , data = data_learning,, dist = "loglogistic")
summary(srFit_loglog)

## Gaussian
srFit_gaus <- survreg(Surv(time_max, observed) ~  sexe +as.factor(generation_group) , data = data_learning,  dist = "gaussian")
summary(srFit_gauss)

## Weibull 
srFit_weibull <- survreg(Surv(time_max, observed) ~  sexe + as.factor(generation_group) , data = data_learning, dist = "weibull")
summary(srFit_weibull)

a <- 1/srFit_weibull$scale 
b <- exp( coef(srFit_weibull) )
y2 <- b * ( -log( 1-runif(1000) ) ) ^(1/a)
plot(sort(y2), main="Conditional Weibull Hazard",
     xlab="time", ylab="Hazard")




### II. Fit ###

## Graphical comparison
comp = list(fit=srFit_KM, lam.e=exp(-coef(srFit_exp)), lam.w=exp(-coef(srFit_weibull)), gam=1/srFit_weibull$scale)


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








## II. Estimation ####


attach(data_TTH3)

## II.1 Parametric estimation ####


## Comparison
fit <- survfit(Surv(time_max, observed)~1)
fit.exp <- survreg(Surv(time_max, observed)~1, dist='exponential')
fit.wbl <- survreg(Surv(time_max, observed)~1, dist='weibull')
comp = list(fit=fit, lam.e=exp(-coef(fit.exp)), lam.w=exp(-coef(fit.wbl)), gam=1/fit.wbl$scale)

dev.off()
pdf(paste0(fig_path,"comp.pdf"))
par(mar=c(4,4,1,1))
plot(comp$fit, conf.int=FALSE, las=1, mark.time=FALSE, col='grey60',lwd=3, 
     ylab = "Survival",xlab = "Duration in grade")
tt <- seq(0, max(comp$fit$time), len=99)
lines(tt, pexp(tt, comp$lam.e, low=FALSE), col="grey20", lwd=3)
lines(tt, pweibull(tt, comp$gam, 1/comp$lam.w, low=FALSE), col="black", , lwd=3)
legend("bottomleft", legend = c("KM","Exponential", "Weibull"), lty = 1, col = c("grey60", "grey20", "black"), lwd = 3)
dev.off()



detach(data_TTH3)
*
  ## II.2  Cox PH with time-fixed variable ####
attach(data_TTH3)

my.surv   <- Surv(time_max, observed)
coxph.fit1 <- coxph(my.surv ~ sexe + as.factor(generation_group), method="breslow") #sexe +
coxph.fit3 <- coxph(my.surv ~ sexe +  as.factor(generation_group), method="efron")

plot(survfit(coxph.fit1), ylim=c(0, 1), xlab="Year",ylab="Proportion in grade")

detach(data_TTH3)

## II.3  Cox PH with time-dependent variable ####

## II.3.1  0/1 Treatment ####

N <- dim(data_TTH3)[1]
t1 <- rep(0, N+sum(data_TTH3$time_max >= 5)) # initialize start time at 0
t2 <- rep(-1, length(t1)) # build vector for end times
d <- rep(-1, length(t1)) # whether event was censored
generation <- rep(-1, length(t1)) # generation covariate
duree_legale_depassee <- rep(FALSE, length(t1)) # initialize duree_legale_depassee at FALSE

j <- 1
for(ii in 1:dim(data_TTH3)[1]){
  if(data_TTH3$time_max[ii] < 5){ # duree non depassee, copy survival record
    print('hello')
    t2[j] <- data_TTH3$time_max[ii]
    d[j] <- data_TTH3$observed[ii]
    generation[j] <- data_TTH3$generation[ii]
    j <- j+1
  } else { # intervention, split records
    print('bye')
    generation[j+0:1] <- data_TTH3$generation[ii] # gender is same for each time
    d[j] <- 0 # pas de fin obs avant 5 ans
    d[j+1] <- data_TTH3$observed[ii] 
    duree_legale_depassee[j+1] <- TRUE 
    t2[j] <- 5 
    t1[j+1] <- 5 # start of post-intervention
    t2[j+1] <- data_TTH3$time_max[ii] # end of post-intervention
    j <- j+2 # two records added
  }
}

mySurv <- Surv(t1, t2, d)
myCPH <- coxph(mySurv ~ generation + factor(duree_legale_depassee))

"ERREUR: In coxph(mySurv ~ generation + factor(duree_legale_depassee)) :
X matrix deemed to be singular; variable 2"



## II.3.2  Distance to threshold dummies ####
# Mise au format pour l'estimation avec varying
data_TTH3_long <-  data_long[which(data_long$c_cir == 'TTH3'), c("ident","annee", "sexe", "generation_group","observed", "exit_status", "right_censoring", "time_min", "time_max")]

# Count de la duree
data_TTH3_long$duree_ref= 5
data_TTH3_long$a = 1
data_TTH3_long$count = ave(data_TTH3_long$a, data_TTH3_long$ident, FUN = cumsum)
data_TTH3_long$start = data_TTH3_long$count -1
data_TTH3_long$stop  = data_TTH3_long$count 
# Ind de départ 
data_TTH3_long$max_annee = ave(data_TTH3_long$annee, data_TTH3_long$ident, FUN = max)
data_TTH3_long$exit.time  = ifelse(data_TTH3_long$max_annee == data_TTH3_long$annee & data_TTH3_long$observed == 1, 1 ,0)
# Dummies pour la distance 
data_TTH3_long$dist = data_TTH3_long$count - data_TTH3_long$duree_ref
data_TTH3_long$Im5 = ifelse(data_TTH3_long$dist == -5, 1, 0)
data_TTH3_long$Im4 = ifelse(data_TTH3_long$dist == -4, 1, 0)
data_TTH3_long$Im3 = ifelse(data_TTH3_long$dist == -3, 1, 0)
data_TTH3_long$Im2 = ifelse(data_TTH3_long$dist == -2, 1, 0)
data_TTH3_long$Im1 = ifelse(data_TTH3_long$dist == -1, 1, 0)
data_TTH3_long$Ip5 = ifelse(data_TTH3_long$dist == 5, 1, 0)
data_TTH3_long$Ip4 = ifelse(data_TTH3_long$dist == 4, 1, 0)
data_TTH3_long$Ip3 = ifelse(data_TTH3_long$dist == 3, 1, 0)
data_TTH3_long$Ip2 = ifelse(data_TTH3_long$dist == 2, 1, 0)
data_TTH3_long$Ip1 = ifelse(data_TTH3_long$dist == 1, 1, 0)
data_TTH3_long$I0 = ifelse(data_TTH3_long$dist == 0, 1, 0)

coxph.fit1 = coxph(Surv(start, stop, exit.time) ~  sexe + generation_group + I0,
                   data=data_TTH3_long)


# tutoriel
data(relapse)

N <- dim(relapse)[1]
t1 <- rep(0, N+sum(!is.na(relapse$int))) # initialize start time at 0
t2 <- rep(-1, length(t1)) # build vector for end times
d <- rep(-1, length(t1)) # whether event was censored
g <- rep(-1, length(t1)) # gender covariate
i <- rep(FALSE, length(t1)) # initialize intervention at FALSE

j <- 1
for(ii in 1:dim(relapse)[1]){
  if(is.na(relapse$int[ii])){ # no intervention, copy survival record
    t2[j] <- relapse$event[ii]
    d[j] <- relapse$delta[ii]
    g[j] <- relapse$gender[ii]
    j <- j+1
  } else { # intervention, split records
    g[j+0:1] <- relapse$gender[ii] # gender is same for each time
    d[j] <- 0 # no relapse observed pre-intervention
    d[j+1] <- relapse$delta[ii] # relapse occur post-intervention?
    i[j+1] <- TRUE # intervention covariate, post-intervention
    t2[j] <- relapse$int[ii]-1 # end of pre-intervention
    t1[j+1] <- relapse$int[ii]-1 # start of post-intervention
    t2[j+1] <- relapse$event[ii] # end of post-intervention
    j <- j+2 # two records added
  }
}

mySurv <- Surv(t1, t2, d) # pg 3 discusses left-trunc. right-cens. data
myCPH <- coxph(mySurv ~ g + i)

