




################ Estimation by logit ################


data_est = data_min
data_est = data_est[which(data_est$left_censored == F & data_est$annee >= 2013 & data_est$annee <= 2014),]


tirage<-function(var)
{
  t<-rbinom(1,1,var) # Loi binomiale 
  return(t)
}


#### 0. Variable creations ####

# Distance variables
data_est$I_echelon = ifelse(data_est$echelon >= data_est$E_choice, 1, 0) 
data_est$I_grade = ifelse(data_est$time >= data_est$D_choice, 1, 0) 
data_est$dist_an_aff = data_est$annee - data_est$an_aff +1 
data_est$I_grade[which(data_est$c_cir_2011 == "TTH2")] = ifelse(data_est$dist_an_aff[which(data_est$c_cir_2011 == "TTH2")] >= data_est$D_choice[which(data_est$c_cir_2011 == "TTH2")], 1, 0) 
data_est$I_both = ifelse(data_est$time >= data_est$D_choice & data_est$echelon >= data_est$E_choice, 1, 0) 

data_est$c_cir = factor(data_est$c_cir)


data_est$time2 = data_est$time^2 
data_est$time3 = data_est$time^3 


#### I. Binary model ####


## I.1 Estimation ####

tr.log1 <- glm(exit_status2 ~ 1,
               data=data_est ,x=T,family=binomial("logit"))

tr.log2 <- glm(exit_status2 ~ sexe + factor(generation_group) + factor(c_cir_2011),
               data=data_est ,x=T,family=binomial("logit"))

tr.log3 <- glm(exit_status2 ~ sexe + factor(generation_group) + factor(c_cir_2011) + I_grade ,
               data=data_est ,x=T,family=binomial("logit"))

tr.log4 <- glm(exit_status2 ~ sexe + factor(generation_group) + factor(c_cir_2011) + I_echelon,
               data=data_est ,x=T,family=binomial("logit"))

tr.log5 <- glm(exit_status2 ~ sexe + factor(generation_group) + factor(c_cir_2011) + 
                 I_echelon + I_grade+ I_echelon:I_grade,
               data=data_est ,x=T,family=binomial("logit"))


tr.log6 <- glm(exit_status2 ~ sexe + factor(generation_group) + factor(c_cir_2011) + time+time2 + time3+ echelon + 
                 I_echelon + I_grade+ I_echelon:I_grade,
               data=data_est ,x=T,family=binomial("logit"))

## I.2 Simulation ####

## I.2.1 2015 ##
data_learning = data_est[which(data_est$annee == 2014),]
data_test     = data_est[which(data_est$annee == 2014),]

model <- glm(exit_status2 ~ sexe + factor(generation_group) + factor(c_cir_2011) + an_aff + echelon +
                 I_echelon + I_grade+ I_echelon:I_grade,
               data=data_learning ,x=T, family=binomial("logit"))

# Sorties simulées
data_test$yhat1    <- predict(model, data_test,type = "response") 
data_test$exit_hat <- as.numeric(lapply(data_test$yhat1 , tirage))


summary(data_test$exit_hat)
summary(data_test$exit_status2)
summary(data_test$exit_hat[which(data_test$c_cir_2011 == "TTH1")])
summary(data_test$exit_status2[which(data_test$c_cir_2011 == "TTH1")])
summary(data_test$exit_hat[which(data_test$c_cir_2011 == "TTH2")])
summary(data_test$exit_status2[which(data_test$c_cir_2011 == "TTH2")])
summary(data_test$exit_hat[which(data_test$c_cir_2011 == "TTH3")])
summary(data_test$exit_status2[which(data_test$c_cir_2011 == "TTH3")])
summary(data_test$exit_hat[which(data_test$c_cir_2011 == "TTH4")])
summary(data_test$exit_status2[which(data_test$c_cir_2011 == "TTH4")])


## I.2.2 Two datasets ##

list_id = unique(data_est$ident)
list_learning = sample(list_id, ceiling(length(list_id)/2))
list_test = setdiff(list_id, list_learning)
data_learning = data_est[which(is.element(data_est$ident, list_learning)),]
data_test     = data_est[which(is.element(data_est$ident, list_test)),]

model <- glm(exit_status2 ~ sexe + factor(generation_group) + factor(c_cir_2011) + time + an_aff + echelon +
               I_echelon + I_grade+ I_echelon:I_grade,,
             data=data_learning ,x=T, family=binomial("logit"))


### Predicted exit date
data_test$yhat1    <- predict(model, data_test, type = "response") 
data_test$ind_exit = 0
data_test$exit_hat = 0

for (y in seq(2011, 2014, 1))
{
list = which(data_test$annee == y & data_test$ind_exit == 0)
data_test$exit_hat[list] = as.numeric(lapply(data_test$yhat1[list]  , tirage))
ident_exit = data_test$ident[which(data_test$exit_hat == 1)]
data_test$ind_exit[which(is.element(data_test$ident, ident_exit))] = 1
}

observed_exit  = tapply(data_test$annee*data_test$exit_status2, data_test$ident, FUN = max)
predicted_exit = tapply(data_test$annee*data_test$exit_hat,     data_test$ident, FUN = max)

table(observed_exit)
table(predicted_exit)


# Observed/predicted survival between 2011 and 2015
annee <- seq(2011, 2015, 1)
survival = matrix(ncol = length(annee), nrow = 2)
hazard_rate = matrix(ncol = length(annee), nrow = 2)

observed_exit[which(observed_exit == 0)] = 9999
predicted_exit[which(predicted_exit == 0)] = 9999

for (y in (1:length(annee)))
{
  n = length(observed_exit)
  # Survival Rate
  survival[1, y] = length(which(observed_exit >= annee[y] | is.na(observed_exit)))/n
  survival[2, y] = length(which(predicted_exit >= annee[y] | is.na(predicted_exit)))/n
  # Hazard Rate
  if (y < length(annee))
  {
    hazard_rate[1, y] = length(which(observed_exit == annee[y]))/length(which(observed_exit >= annee[y]))
    hazard_rate[2, y] = length(which(predicted_exit == annee[y]))/length(which(predicted_exit >= annee[y]))
  }
}  


# Plot
plot(annee, rep(NA, length(annee)), ylim = c(0,1),  ylab = "Survival rate",xlab = "Year")
lines(annee, survival[1, ], col="grey20", lwd=3)
lines(annee, survival[2, ], col="grey50", lwd=3)
legend("bottomleft", legend = c("Observed", "Simulated"), 
       lty = 1, col = c("grey20", "grey80"), lwd = 3)


# Plot
plot(annee, rep(NA, length(annee)), ylim = c(0,0.4),  ylab = "Hazard rate",xlab = "Year")
lines(annee, hazard_rate[1, ], col="grey20", lwd=3)
lines(annee, hazard_rate[2, ], col="grey50", lwd=3)
legend("topleft", legend = c("Observed", "Simulated"), 
       lty = 1, col = c("grey20", "grey80"), lwd = 3)




