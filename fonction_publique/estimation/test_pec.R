## Test pec package


## simulate some learning and some validation data
learndat <- SimSurv(100)
valdat <- SimSurv(100)
## use the learning data to fit a Cox model
library(survival)
fitCox <- coxph(Surv(time,status)~X1+X2,data=learndat)

srFit_weibull <- survreg(Surv(time_max, observed) ~  1 , data = data_learning, dist = "weibull")
summary(srFit_weibull)

srFit_weibull2 <- psm(Surv(time_max, observed) ~  1 , data = data_learning, dist = "weibull")
summary(srFit_weibull2)


f <- psm(Surv(d.time,death) ~ sex*pol(age,2), 
         dist='lognormal')

fitCox2 <- coxph(Surv(time_max,observed)~ 1 ,data=data_learning)


## suppose we want to predict the survival probabilities for all patients
## in the validation data at the following time points:
## 0, 12, 24, 36, 48, 60
psurv <- predictSurvProb(fitCox,newdata=valdat,times=seq(0,12,12))



srFit_exp <- psm(Surv(time_max, observed) ~  1 + generation_group , data = data_learning, dist = "exponential")
srFit_weibull <- psm(Surv(time_max, observed) ~  1 + generation_group , data = data_learning, dist = "weibull")
psurv2 <- predictSurvProb(srFit_weibull,newdata=data_test, train.data = data_learning, times=seq(1,9,1))
plotPredictSurvProb(srFit_weibull,newdata=data_test, train.data = data_learning, times=seq(1,8,1))
plotPredictSurvProb(srFit_exp,newdata=data_test, train.data = data_learning, times=seq(1,8,1))


library(survival)
library(rms)
library(pec)

f1 <-  psm(Surv(time_max, observed) ~  1 + generation_group, data = data_learning, dist = "weibull")
f2 <-  psm(Surv(time_max, observed) ~  1 + generation_group, data = data_learning, dist = "exponential")
brier <- pec(list("Weibull"=f1,"Exponential"=f2), data=data_learning,formula=Surv(time_max,observed)~1)
print(brier)
plot(brier)

data(pbc)
pbc <- pbc[sample(1:NROW(pbc),size=100),]

f1 <- psm(Surv(time_max,obsee=0)~edema+log(bili)+age+sex+albumin,data=data_learning)
f2 <- coxph(Surv(time,status!=0)~edema+log(bili)+age+sex+albumin,data=data_learning)
f3 <- cph(Surv(time,status!=0)~edema+log(bili)+age+sex+albumin,data=pbc,surv=TRUE)
brier <- pec(list("Weibull"=f1,"CoxPH"=f2,"CPH"=f3),data=pbc,formula=Surv(time,status!=0)~1)
print(brier)
plot(brier)


