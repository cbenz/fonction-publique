




################ Estimation by logit ################



source(paste0(wd, "0_work_on_data.R"))
datasets = load_and_clean(data_path, "data_ATT_2002_2015_2.csv")
data_id = datasets[[1]]
data_max = datasets[[2]]
data_min = datasets[[3]]


data_est = data_min
data_est = data_est[which(data_est$left_censored == F & data_est$annee >= 2011 & data_est$annee <= 2014),]


#### 0. Variable creations ####

data_est$dist_an_aff = data_est$annee - data_est$an_aff +1 
grade_modif = which(data_est$c_cir_2011 == "TTH1" | data_est$c_cir_2011 == "TTH2")

data_est$time2 = data_est$time
data_est$time2[grade_modif] = data_est$dist_an_aff[grade_modif] 

# Distance variables
data_est$I_echC = ifelse(data_est$echelon >= data_est$E_choice, 1, 0) 
data_est$I_gradeC   = ifelse(data_est$time2 >= data_est$D_choice, 1, 0) 
data_est$I_gradeC   = ifelse(data_est$time2 >= data_est$D_choice, 1, 0) 


data_est$I_echE = ifelse(data_est$echelon >= data_est$E_exam & data_est$c_cir_2011 == "TTH1", 1, 0) 
data_est$I_gradeE   = ifelse(data_est$time2 >= data_est$D_exam & data_est$c_cir_2011 == "TTH1", 1, 0) 


data_est$c_cir = factor(data_est$c_cir)
data_est$time2 = data_est$time^2 
data_est$time3 = data_est$time^3 


data_est$generation_group = factor(data_est$generation_group)
data_est$c_cir_2011 = factor(data_est$c_cir_2011)

#### I. Binary model ####

## I.1 Estimation ####

log1 <- glm(exit_status2 ~  I_echC + I_gradeC+ I_echC:I_gradeC,
            data=data_est ,x=T,family=binomial("logit"))


log2 <- glm(exit_status2 ~   I_echE + I_gradeE+ I_echE:I_gradeE,
            data=data_est ,x=T,family=binomial("logit"))

log3 <- glm(exit_status2 ~  I_echC + I_gradeC+ I_echC:I_gradeC + 
              I_echE + I_gradeE+ I_echE:I_gradeE,
            data=data_est ,x=T,family=binomial("logit"))

log4 <- glm(exit_status2 ~ sexe + generation_group + c_cir_2011 + 
              I_echC + I_gradeC+ I_echC:I_gradeC +
              I_echE + I_gradeE+ I_echE:I_gradeE,
            data=data_est ,x=T,family=binomial("logit"))

log5 <- glm(exit_status2 ~ sexe +generation_group + c_cir_2011 + 
              time + echelon + an_aff + 
              I_echC + I_gradeC+ I_echC:I_gradeC +
              I_echE + I_gradeE+ I_echE:I_gradeE,
            data=data_est ,x=T,family=binomial("logit"))


## Before/after
l1 <- extract.glm(log1, include.aic = F, include.bic=F, include.loglik = F, include.deviance = F)
l2 <- extract.glm(log2, include.aic = F, include.bic=F, include.loglik = F, include.deviance = F)
l3 <- extract.glm(log3, include.aic = F, include.bic=F, include.loglik = F, include.deviance = F)
l4 <- extract.glm(log4, include.aic = F, include.bic=F, include.loglik = F, include.deviance = F)
l5 <- extract.glm(log5, include.aic = F, include.bic=F, include.loglik = F, include.deviance = F)


list_models <- list(l1, l2, l3, l4, l5)
# name.map <- list("I_gradeC"="\\$\mathbb{1}_{{cond.grade1}}\\$","I_gradeE"="\\$\mathbb{1}_{{cond.grade2}}\\$",
#                  "I_echC"="\\$\mathbb{1}_{{cond.ech1}}\\$","I_echE"="\\$\mathbb{1}_{{cond.ech2}}\\$",
#                  "I_echC"="\\$\mathbb{1}_{{cond.ech1}}\\$","I_echE"="\\$\mathbb{1}_{{cond.ech2}}\\$")
# oldnames <- all.varnames.dammit(list_models) 
omit_var = paste0("(Intercept)|sexeM|generation_group7|generation_group8|generation_group9|",
                   "time|echelon|an_aff|c_cir_2011TTH2|c_cir_2011TTH3|c_cir_2011TTH4")               

print(texreg(list_models,
       caption.above=F, 
       float.pos = "!ht",
       digit=2,
       only.content= T,
       stars = c(0.01, 0.05, 0.1),
       #custom.coef.names=ror$ccn,  omit.coef=ror$oc, reorder.coef=ror$rc,
       omit.coef = omit_var,
       booktabs=T), only.contents = T)



## I.2 Interpretation ####
log5 <- glm(exit_status2 ~ sexe +generation_group + c_cir_2011 + 
              time + echelon + an_aff + 
              I_echC + I_gradeC+ I_echC:I_gradeC +
              I_echE + I_gradeE+ I_echE:I_gradeE,
            data=data_est ,x=T,family=binomial("logit"))
mfx1log5 <- logitmfx(exit_status2 ~ sexe +generation_group + c_cir_2011 + 
                       time + echelon + an_aff + 
                       I_echC + I_gradeC+ I_echC:I_gradeC +
                       I_echE + I_gradeE+ I_echE:I_gradeE,
                     data=data_est, atmean = F)
mfx2log5 <- logitmfx(exit_status2 ~ sexe +generation_group + c_cir_2011 + 
                  time + echelon + an_aff + 
                  I_echC + I_gradeC+ I_echC:I_gradeC +
                  I_echE + I_gradeE+ I_echE:I_gradeE,
                data=data_est)


names = variable.names(log5)[12:17]
coef1 = coef(log5)[12:17]
odd = exp(coef(log5)[12:17])
me1 = mfx1log5$mfxest[11:16]
me2 = mfx2log5$mfxest[11:16]

table = matrix(ncol = 6, nrow = 4)
table[1,] = coef1
table[2,] = odd
table[3,] = me1
table[4,] = me2
colnames(table) = names
rownames(table) = c('Coefficient', "Odd ratio", "Marginal effect", "Average partial effect")

print(xtable(table,align="lcccccc",nrow = nrow(table), ncol=ncol(table)+1, byrow=T, digits = 3),
      sanitize.text.function=identity,size="\\footnotesize", 
      only.contents=F, include.colnames = T)



## I.2 Simulation ####

list_id = unique(data_est$ident)
list_learning = sample(list_id, ceiling(length(list_id)/2))
list_test = setdiff(list_id, list_learning)
data_learning = data_est[which(is.element(data_est$ident, list_learning)),]
data_test     = data_est[which(is.element(data_est$ident, list_test)),]


## 2011 ####
data_learning1 = data_learning[which(data_test$annee >= 2011),]
data_test1     = data_test[which(data_test$annee == 2011),]

model0 <- glm(exit_status2 ~  1,
            data=data_learning1 ,x=T,family=binomial("logit"))

model1 <- glm(exit_status2 ~  I_echC + I_gradeC+ I_echC:I_gradeC + 
              I_echE + I_gradeE+ I_echE:I_gradeE,
            data=data_learning1 ,x=T,family=binomial("logit"))

model2 <- glm(exit_status2 ~ sexe + generation_group + c_cir_2011 + 
              I_echC + I_gradeC+ I_echC:I_gradeC +
              I_echE + I_gradeE+ I_echE:I_gradeE,
            data=data_learning1 ,x=T,family=binomial("logit"))

model3 <- glm(exit_status2 ~ sexe +generation_group + c_cir_2011 + 
              time + echelon + an_aff + 
              I_echC + I_gradeC+ I_echC:I_gradeC +
              I_echE + I_gradeE+ I_echE:I_gradeE,
            data=data_learning1 ,x=T,family=binomial("logit"))

# Simulated exit
data_test1$yhat0     <- predict(model0, data_test1,type = "response") 
data_test1$yhat1     <- predict(model1, data_test1,type = "response") 
data_test1$yhat2     <- predict(model2, data_test1,type = "response") 
data_test1$yhat3     <- predict(model2, data_test1,type = "response") 
data_test1$exit_hat0 <- as.numeric(lapply(data_test1$yhat0 , tirage))
data_test1$exit_hat1 <- as.numeric(lapply(data_test1$yhat1 , tirage))
data_test1$exit_hat2 <- as.numeric(lapply(data_test1$yhat2 , tirage))
data_test1$exit_hat3 <- as.numeric(lapply(data_test1$yhat3 , tirage))



# Sorties
table_fit = matrix(ncol = 4, nrow = 8)
list_model = list(model0, model1, model2, model3)
for (m in 1:length(list_model))
{
model = list_model[[m]]  
# AIC/BIC
table_fit[1, m] = AIC(model)
table_fit[2, m] = BIC(model) 
# Predict/Observed
data_test1$yhat     <- predict(model, data_test1,type = "response") 
data_test1$exit_hat <- as.numeric(lapply(data_test1$yhat , tirage))
table_fit[3, m] = mean(data_test1$exit_hat)
table_fit[4, m] = (mean(data_test1$exit_hat)-mean(data_test1$exit_status2))/mean(data_test1$exit_status2)

table_fit[5, m] = length(which(data_test1$exit_hat == 1 & data_test1$exit_status2 == 1))/length(which(data_test1$exit_status2 == 1))
table_fit[6, m] = length(which(data_test1$exit_hat == 0 & data_test1$exit_status2 == 0))/length(which(data_test1$exit_status2 == 0))
table_fit[7, m] = length(which(data_test1$exit_hat == 0 & data_test1$exit_status2 == 1))/length(which(data_test1$exit_status2 == 1))
table_fit[8, m] = length(which(data_test1$exit_hat == 1 & data_test1$exit_status2 == 0))/length(which(data_test1$exit_status2 == 0))
}


colnames(table_fit) = c('Null model', 'Model M3', 'Model M4', 'Model M5')
rownames(table_fit) = c('AIC', "BIC", "Prop of exit", "Diff pred. vs. obs", 
                        "\\% true positive", "\\% true negative", "\\% false negative", "\\% false positive")

print(xtable(table_fit,align="lcccc",nrow = nrow(table_fit), ncol=ncol(table_fit)+1, byrow=T, digits = 3),
      sanitize.text.function=identity,size="\\footnotesize", hline.after = c(0, 2, 4),
      only.contents=F, include.colnames = T)



## Fit by grade


data_test1$yhat     <- predict(model0, data_test1,type = "response") 
data_test1$exit_hat <- as.numeric(lapply(data_test1$yhat , tirage)) 
# Sorties
table_fit_by_grade = matrix(ncol = 5, nrow = 6)
grade = list("all", "TTH1", "TTH2", "TTH3", "TTH4")
for (g in 1:length(grade))
{
  if (grade[g] == "all"){subdata = data_test1}
  else{subdata = data_test1[which(data_test1$c_cir_2011 == grade[g]),]}
  # Predict/Observed
  table_fit_by_grade[1, g] = mean(subdata$exit_hat)
  table_fit_by_grade[2, g] = (mean(subdata$exit_hat)-mean(subdata$exit_status2))/mean(subdata$exit_status2)
  table_fit_by_grade[3, g] = length(which(subdata$exit_hat == 1 & subdata$exit_status2 == 1))/length(which(subdata$exit_status2 == 1))
  table_fit_by_grade[4, g] = length(which(subdata$exit_hat == 0 & subdata$exit_status2 == 0))/length(which(subdata$exit_status2 == 0))
  table_fit_by_grade[5, g] = length(which(subdata$exit_hat == 0 & subdata$exit_status2 == 1))/length(which(subdata$exit_status2 == 1))
  table_fit_by_grade[6, g] = length(which(subdata$exit_hat == 1 & subdata$exit_status2 == 0))/length(which(subdata$exit_status2 == 0))
}


colnames(table_fit_by_grade) = c('All', 'TTH1', 'TTH2', 'TTH3', 'TTH4')
rownames(table_fit_by_grade) = c("Prop of exit", "Diff pred. vs. obs", 
                                 "\\% true positive", "\\% true negative", "\\% false negative", "\\% false positive")

print(xtable(table_fit_by_grade,align="lccccc",nrow = nrow(table_fit_by_grade), 
             ncol=ncol(table_fit_by_grade)+1, byrow=T, digits = 3),
      sanitize.text.function=identity,size="\\footnotesize", hline.after = c(0, 2, 4),
      only.contents=T, include.colnames = T)



data_test1$yhat     <- predict(model3, data_test1,type = "response") 
data_test1$exit_hat <- as.numeric(lapply(data_test1$yhat , tirage)) 
# Sorties
table_fit_by_grade = matrix(ncol = 5, nrow = 6)
grade = list("all", "TTH1", "TTH2", "TTH3", "TTH4")
for (g in 1:length(grade))
{
  if (grade[g] == "all"){subdata = data_test1}
  else{subdata = data_test1[which(data_test1$c_cir_2011 == grade[g]),]}
  # Predict/Observed
  table_fit_by_grade[1, g] = mean(subdata$exit_hat)
  table_fit_by_grade[2, g] = (mean(subdata$exit_hat)-mean(subdata$exit_status2))/mean(subdata$exit_status2)
  table_fit_by_grade[3, g] = length(which(subdata$exit_hat == 1 & subdata$exit_status2 == 1))/length(which(subdata$exit_status2 == 1))
  table_fit_by_grade[4, g] = length(which(subdata$exit_hat == 0 & subdata$exit_status2 == 0))/length(which(subdata$exit_status2 == 0))
  table_fit_by_grade[5, g] = length(which(subdata$exit_hat == 0 & subdata$exit_status2 == 1))/length(which(subdata$exit_status2 == 1))
  table_fit_by_grade[6, g] = length(which(subdata$exit_hat == 1 & subdata$exit_status2 == 0))/length(which(subdata$exit_status2 == 0))
}


colnames(table_fit_by_grade) = c('All', 'TTH1', 'TTH2', 'TTH3', 'TTH4')
rownames(table_fit_by_grade) = c("Prop of exit", "Diff pred. vs. obs", 
                        "\\% true positive", "\\% true negative", "\\% false negative", "\\% false positive")

print(xtable(table_fit_by_grade,align="lccccc",nrow = nrow(table_fit_by_grade), 
             ncol=ncol(table_fit_by_grade)+1, byrow=T, digits = 3),
      sanitize.text.function=identity,size="\\footnotesize", hline.after = c(0, 2, 4),
      only.contents=T, include.colnames = T)









data_learning1 = data_learning[which(data_learning$c_cir_2011 == "TTH3" & data_learning$generation_group != 9),]
data_test1     = data_test[which(data_test$annee == 2011 & data_test$c_cir_2011 == "TTH3" & data_test$generation_group != 9),]

model0 <- glm(exit_status2 ~ 1,
             data=data_learning1 ,x=T, family=binomial("logit"))
model1 <- glm(exit_status2 ~ sexe + factor(generation_group),
                data=data_learning1, x=T, family=binomial("logit"))
model2 <- glm(exit_status2 ~ sexe + factor(generation_group) + 
                 I_ech + I_grade+ I_ech:I_grade,
               data=data_learning1, x=T, family=binomial("logit"))

# Sorties simulées
data_test1$yhat0     <- predict(model0, data_test1,type = "response") 
data_test1$yhat1     <- predict(model1, data_test1,type = "response") 
data_test1$yhat2     <- predict(model2, data_test1,type = "response") 
data_test1$exit_hat0 <- as.numeric(lapply(data_test1$yhat0 , tirage))
data_test1$exit_hat1 <- as.numeric(lapply(data_test1$yhat1 , tirage))
data_test1$exit_hat2 <- as.numeric(lapply(data_test1$yhat2 , tirage))


summary(data_test1$exit_hat0)
summary(data_test1$exit_hat1)
summary(data_test1$exit_hat2)
summary(data_test1$exit_status2)
table(data_test1$exit_hat0, data_test1$exit_status2)
table(data_test1$exit_hat1, data_test1$exit_status2)
table(data_test1$exit_hat2, data_test1$exit_status2)

## 2011-2014 ##

model0 <- glm(exit_status2 ~1,
              data = data_learning,x=T, family=binomial("logit"))
model1 <- glm(exit_status2 ~ sexe + factor(generation_group) + factor(c_cir_2011) + an_aff + echelon +
                I_ech + I_grade+ I_ech:I_grade,
              data = data_learning[which(data_learning$annee == 2011),] ,x=T, family=binomial("logit"))
model2 <- glm(exit_status2 ~ sexe + factor(generation_group) + factor(c_cir_2011) +  an_aff + echelon +
                I_ech + I_grade+ I_ech:I_grade,
              data=data_learning ,x=T, family=binomial("logit"))



### Predicted exit date
### Predicted exit date
data_test$yhat0    <- predict(model0, data_test, type = "response") 
data_test$yhat1    <- predict(model1, data_test, type = "response") 
data_test$yhat2    <- predict(model2, data_test, type = "response") 
data_test$ind_exit0 = 0
data_test$ind_exit1 = 0
data_test$ind_exit2 = 0
data_test$exit_hat0 = 0
data_test$exit_hat1 = 0
data_test$exit_hat2 = 0

for (y in seq(2011, 2014, 1))
{
# Model 0  
list0 = which(data_test$annee == y & data_test$ind_exit0 == 0)
data_test$exit_hat0[list0] = as.numeric(lapply(data_test$yhat0[list0]  , tirage))
print(mean(as.numeric(lapply(data_test$yhat0[list0]  , tirage))))
ident_exit0 = data_test$ident[which(data_test$exit_hat0 == 1)]
data_test$ind_exit0[which(is.element(data_test$ident, ident_exit0) & data_test$annee == y)] = 1
}


# Model 1  
list1 = which(data_test$annee == y & data_test$ind_exit1 == 0)
data_test$exit_hat1[list1] = as.numeric(lapply(data_test$yhat1[list1]  , tirage))
ident_exit1 = data_test$ident[which(data_test$exit_hat1 == 1)]
data_test$ind_exit1[which(is.element(data_test$ident, ident_exit1))] = 1
# Model 2  
list2 = which(data_test$annee == y & data_test$ind_exit2 == 0)
data_test$exit_hat2[list2] = as.numeric(lapply(data_test$yhat2[list2]  , tirage))
ident_exit2 = data_test$ident[which(data_test$exit_hat2 == 1)]
data_test$ind_exit2[which(is.element(data_test$ident, ident_exit2))] = 1
}

observed_exit  = tapply(data_test$annee*data_test$exit_status2, data_test$ident, FUN = max)
predicted_exit1 = tapply(data_test$annee*data_test$exit_hat1,     data_test$ident, FUN = max)
predicted_exit2 = tapply(data_test$annee*data_test$exit_hat2,     data_test$ident, FUN = max)
predicted_exit0 = tapply(data_test$annee*data_test$exit_hat0,     data_test$ident, FUN = max)

table(observed_exit)
table(predicted_exit0)
table(predicted_exit1)
table(predicted_exit2)




# Observed/predicted survival between 2011 and 2015
annee <- seq(2011, 2015, 1)
survival = matrix(ncol = length(annee), nrow = 4)
hazard_rate = matrix(ncol = length(annee), nrow = 4)

observed_exit[which(observed_exit == 0)] = 9999
predicted_exit1[which(predicted_exit1 == 0)] = 9999
predicted_exit2[which(predicted_exit2 == 0)] = 9999
predicted_exit0[which(predicted_exit0 == 0)] = 9999



for (y in (1:length(annee)))
{
  n = length(observed_exit)
  # Survival Rate
  survival[1, y] = length(which(observed_exit >= annee[y] | is.na(observed_exit)))/n
  survival[2, y] = length(which(predicted_exit1 >= annee[y] | is.na(predicted_exit1)))/n
  survival[3, y] = length(which(predicted_exit2 >= annee[y] | is.na(predicted_exit2)))/n
  survival[4, y] = length(which(predicted_exit0 >= annee[y] | is.na(predicted_exit0)))/n
  # Hazard Rate
  if (y < length(annee))
  {
    hazard_rate[1, y] = length(which(observed_exit == annee[y]))/length(which(observed_exit >= annee[y]))
    hazard_rate[2, y] = length(which(predicted_exit1 == annee[y]))/length(which(predicted_exit1 >= annee[y]))
    hazard_rate[3, y] = length(which(predicted_exit2 == annee[y]))/length(which(predicted_exit2 >= annee[y]))
    hazard_rate[4, y] = length(which(predicted_exit0 == annee[y]))/length(which(predicted_exit0 >= annee[y]))
  }
}  


# Plot
plot(annee, rep(NA, length(annee)), ylim = c(0,1),  ylab = "Survival rate",xlab = "Year")
lines(annee, survival[1, ], col="grey20", lwd=3)
lines(annee, survival[2, ], col="grey50", lwd=3)
lines(annee, survival[3, ], col="grey80", lwd=3)
lines(annee, survival[4, ], col="black", lwd=3, lty = 3)
legend("bottomleft", legend = c("Observed", "Simulated"), 
       lty = 1, col = c("grey20", "grey80"), lwd = 3)


# Plot
plot(annee, rep(NA, length(annee)), ylim = c(0,0.2),  ylab = "Hazard rate",xlab = "Year")
lines(annee, hazard_rate[1, ], col="grey20", lwd=3)
lines(annee, hazard_rate[2, ], col="grey50", lwd=3)
lines(annee, hazard_rate[3, ], col="grey80", lwd=3)
lines(annee, hazard_rate[4, ], col="black", lwd=3, lty = 3)
legend("topleft", legend = c("Observed", "Simulated"), 
       lty = 1, col = c("grey20", "grey80"), lwd = 3)




