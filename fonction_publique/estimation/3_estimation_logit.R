




######## Estimation by logit ########

data_est = data_min
data_est = data_est[which(data_est$left_censored == F),]


#### 0. Variable creations ####

# Distance variables
data_est$I_echelon = ifelse(data_est$echelon >= data_est$E_choice, 1, 0) 
data_est$I_grade = ifelse(data_est$time >= data_est$D_choice, 1, 0) 
data_est$dist_an_aff = data_est$annee - data_est$an_aff +1 
data_est$I_grade[which(data_est$c_cir_2011 == "TTH2")] = ifelse(data_est$dist_an_aff[which(data_est$c_cir_2011 == "TTH2")] >= data_est$D_choice[which(data_est$c_cir_2011 == "TTH2")], 1, 0) 
data_est$I_both = ifelse(data_est$time >= data_est$D_choice & data_est$echelon >= data_est$E_choice, 1, 0) 

data_est$c_cir = factor(data_est$c_cir)


#### I. Estimation ####


## I.1 Binary model ####

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




#### Estimations 
tr.log0 <- glm(t_liquid ~ 1,
               data=base[which(!is.na(base$Accrual)),],x=T,family=binomial("probit"))

tr.log1 <- glm(t_liquid ~ Accrual ,
               data=base,x=T,family=binomial("probit"))

tr.log2 <- glm(t_liquid ~ Accrual + SSW,
               data=base,x=T,family=binomial("probit"))

tr.log3 <- glm(t_liquid ~ Accrual+SSW + age,
               data=base,x=T,family=binomial("probit"))

tr.log4 <- glm(t_liquid ~ Accrual +SSW + age+ salaire,
               data=base,x=T,family=binomial("probit"))

tr.log5 <- glm(t_liquid ~ Accrual +SSW + age+ salaire + first,
               data=base,x=T,family=binomial("probit"))

tr.log6 <- glm(t_liquid ~ Accrual +SSW + age+ salaire + first + last + sante + sexe  + mar + enf,
               data=base,x=T,family=binomial("probit"))

se       <- robust.se(tr.log6 ,base$rang[which(!is.na(base$Accrual))])[[2]]  
### Tables
logAcc1<-extract.glm2(tr.log1,nullmodel=tr.log0)
logAcc2<-extract.glm2(tr.log2,nullmodel=tr.log0)
logAcc3<-extract.glm2(tr.log3,nullmodel=tr.log0)
logAcc4<-extract.glm2(tr.log4,nullmodel=tr.log0)
logAcc5<-extract.glm2(tr.log5,nullmodel=tr.log0)
logAcc6<-extract.glm2(tr.log6,nullmodel=tr.log0)
R2<-round(as.numeric(100*(1-logLik(tr.log6)/logLik(tr.log0))),2)
#recap[5,5]<-R2

listIV<-list(logAcc1,logAcc2,logAcc3,logAcc4,logAcc6)
lab<- paste0(globalname,"est_table_accrual")
cap <- paste0("Estimation du modèle Accrual ",globalcaption)
texreg(listIV,
       file=paste0(chemingraphe,lab,".tex"),
       caption.above=T,caption=cap,
       label=lab,
       custom.model.names = c("M1","M2", "M3","M4","M5"),
       custom.coef.names = c("Constante", "Accrual (x10000)", "SSW (x100000)", "Age","Salaire (x10000)","AOD", "Age limite","Mauvaise santé","Sexe (ref: homme)","Marié","Avec enfant"),
       float.pos = "!ht"
)

filenameM <-paste0(type,sp,  "IV1_",pas) 
filenameSE<-paste0(type,sp,"seIV1_",pas) 
assign(filenameM, tr.log6)
assign(filenameSE, se)

### Predictions
### Predictions 
# Ages observés
aliq_obs  <- as.numeric(tapply(base2$t_liquid*base2$age, base2$rang, FUN = max) ) 
pliq_obs  <- as.numeric(tapply(base2$t_liquid*base2$pension, base2$rang, FUN = max) )  
TRliq_obs <- as.numeric(tapply(base2$t_liquid*base2$TR, base2$rang, FUN = max) ) 
# Ages simulés
base2$yhat1<-predict(tr.log6,base2,type = "response")    # Calcul des yhat 
pred <- predict_liquid(base2,base2$yhat1)
aliq_sim    <- pred[1,]
pliq_sim    <- pred[2,]
TRliq_sim   <- pred[3,]


plot_comp_fit_param(data_id)
plot_comp_fit_param(data_id, grade = "TTH1")
plot_comp_fit_param(data_id, grade = "TTH2")
plot_comp_fit_param(data_id, grade = "TTH3")
plot_comp_fit_param(data_id, grade = "TTH4")


## II.2  Cox PH with time-fixed variable ####
attach(data_TTH3)

my.surv   <- Surv(time_max, observed)
coxph.fit1 <- coxph(my.surv ~ sexe + as.factor(generation_group), method="breslow") #sexe +
coxph.fit3 <- coxph(my.surv ~ sexe +  as.factor(generation_group), method="efron")

plot(survfit(coxph.fit1), ylim=c(0, 1), xlab="Year",ylab="Proportion in grade")

detach(data_TTH3)


## II.3  Cox PH with time-dependent variables ####

## II.3.1  0/1 Treatment ####

data = data_max[which(data_max$left_censored == F & data_max$c_cir_2011 == "TTH3"),]
data = data_max[which(data_max$left_censored == F & data_max$echelon != - 1),]
data = data_min[which(data_min$left_censored == F),]

# Start/stop
data_est$start = data_est$time - 1
data_est$stop = data_est$time 

# Distance variables
data_est$I_echelon = ifelse(data_est$echelon >= data_est$E_choice, 1, 0) 
data_est$I_grade = ifelse(data_est$time >= data_est$D_choice, 1, 0) 
data_est$dist_an_aff = data_est$annee - data_est$an_aff +1 
data_est$I_grade[which(data_est$c_cir_2011 == "TTH2")] = ifelse(data_est$dist_an_aff[which(data_est$c_cir_2011 == "TTH2")] >= data_est$D_choice[which(data_est$c_cir_2011 == "TTH2")], 1, 0) 
data_est$I_both = ifelse(data_est$time >= data_est$D_choice & data_est$echelon >= data_est$E_choice, 1, 0) 

data_est$c_cir = factor(data_est$c_cir)

coxph.fit1 = coxph(Surv(start, stop, exit_status2) ~  sexe + factor(generation_group) + c_cir_2011 +  I_echelon,
                   data=data)
coxph.fit2 = coxph(Surv(start, stop, exit_status2) ~  sexe + factor(generation_group) + c_cir_2011 +  I_grade,
                   data=data)
coxph.fit3 = coxph(Surv(start, stop, exit_status2) ~  sexe + factor(generation_group) + c_cir_2011 + I_grade + I_echelon + I_grade*I_echelon,
                   data=data)
coxph.fit4 = coxph(Surv(start, stop, exit_status2) ~  sexe + factor(generation_group) + c_cir_2011 +  I_grade*I_echelon,
                   data=data)



##### II.3.2  Distance to threshold dummies (Chetty) #######

data = data_max[which(data_max$left_censored == F & data_max$c_cir_2011 == "TTH3"),]
data = data_max[which(data_max$left_censored == F),]

# Start/stop
data_est$start = data_est$time - 1
data_est$stop = data_est$time 

# Distance variables
data_est$dist_echelon = data_est$echelon - data_est$E_choice 
data_est$dist_grade = data_est$time - data_est$D_choice 

for(d in unique(data_est$dist_echelon)) {
  if (d<=-4){data[paste("dist_echelon_m4",sep="")] <- ifelse(data_est$dist_echelon<=-4,1,0)}
  else if  (d>=4){data[paste("dist_echelon_p4",sep="")] <- ifelse(data_est$dist_echelon>=4,1,0)}
  else if  (d<0){data[paste("dist_echelon_m",abs(d),sep="")] <- ifelse(data_est$dist_echelon==d,1,0)}
  else if  (d==0){data[paste("dist_echelon_",d,sep="")] <- ifelse(data_est$dist_echelon==d,1,0)}
  else if  (d>0){data[paste("dist_echelon_p",d,sep="")] <- ifelse(data_est$dist_echelon==d,1,0)}
}

for(d in unique(data_est$dist_grade)) {
  if (d<=-4){data[paste("dist_grade_m4",sep="")] <- ifelse(data_est$dist_grade<=-4,1,0)}
  else if  (d>=4){data[paste("dist_grade_p4",sep="")] <- ifelse(data_est$dist_grade>=4,1,0)}
  else if  (d<0){data[paste("dist_grade_m",abs(d),sep="")] <- ifelse(data_est$dist_grade==d,1,0)}
  else if  (d==0){data[paste("dist_grade_",d,sep="")] <- ifelse(data_est$dist_grade==d,1,0)}
  else if  (d>0){data[paste("dist_grade_p",d,sep="")] <- ifelse(data_est$dist_grade==d,1,0)}
}




list_id = data_est$ident
list_learning = sample(list_id, ceiling(length(list_id)/2))
list_test = setdiff(list_id, list_learning)
data_learning = data[which(is.element(data_est$ident, list_learning)),]
data_test     = data[which(is.element(data_est$ident, list_test)),]


coxph.fit1 = coxph(Surv(start, stop, exit_status2) ~  sexe + generation_group + c_cir_2011 +
                     dist_echelon_m3 + dist_echelon_m2 + dist_echelon_m1 + dist_echelon_0 + 
                     dist_echelon_p1 + dist_echelon_p2 + dist_echelon_p3 + dist_echelon_p4,
                   data=data_learning)

coxph.fit2 = coxph(Surv(start, stop, exit_status2) ~  sexe + generation_group +
                     dist_grade_m3 + dist_grade_m2 + dist_grade_m1 + dist_grade_0 + 
                     dist_grade_p1 + dist_grade_p2 + dist_grade_p3 + dist_grade_p4,
                   data=data_learning)


data_test$pred = predict(coxph.fit2, newdata=data_test, type = "lp")



## II.4  Parametric estimation with time-dependent variables ####




data = data_min[which(data_min$left_censored == F),]
data_id = data_id[which(data_id$left_censored == F),]
data_id$time = data_id$duree_max




srFit_exp <- flexsurvreg(Surv(start, stop, exit_status2) ~  sexe + generation_group +
                           dist_grade_m3 + dist_grade_m2 + dist_grade_m1 + dist_grade_0 + 
                           dist_grade_p1 + dist_grade_p2 + dist_grade_p3 + dist_grade_p4,
                         data=data_learning, dist = "exponential")





######## III. Simulations ########


# Start/stop
data_est$start = data_est$time - 1
data_est$stop = data_est$time 

# Distance variables
data_est$I_echelon = ifelse(data_est$echelon >= data_est$E_choice, 1, 0) 
data_est$I_grade = ifelse(data_est$time >= data_est$D_choice, 1, 0) 
data_est$dist_an_aff = data_est$annee - data_est$an_aff +1 
data_est$I_grade[which(data_est$c_cir_2011 == "TTH2")] = ifelse(data_est$dist_an_aff[which(data_est$c_cir_2011 == "TTH2")] >= data_est$D_choice[which(data_est$c_cir_2011 == "TTH2")], 1, 0) 
data_est$I_both = ifelse(data_est$time >= data_est$D_choice & data_est$echelon >= data_est$E_choice, 1, 0) 
data_est$c_cir = factor(data_est$c_cir)


list_id = data_est$ident
list_learning = sample(list_id, ceiling(length(list_id)/2))
list_test = setdiff(list_id, list_learning)
data_learning = data[which(is.element(data_est$ident, list_learning)),]
data_test     = data[which(is.element(data_est$ident, list_test)),]


coxph.fit1 = coxph(Surv(start, stop, exit_status2) ~  sexe + factor(generation_group) + c_cir_2011,
                   data=data_learning)
coxph.fit2 = coxph(Surv(start, stop, exit_status2) ~  sexe + factor(generation_group) + c_cir_2011 +  I_echelon,
                   data=data_learning)
coxph.fit3 = coxph(Surv(start, stop, exit_status2) ~  sexe + factor(generation_group) + c_cir_2011 +  I_grade,
                   data=data_learning)
coxph.fit4 = coxph(Surv(start, stop, exit_status2) ~  sexe + factor(generation_group) + c_cir_2011 +  I_grade*I_echelon,
                   data=data_learning)


data_id$time = data_id$duree_min
surv <- Surv(data_id$time, data_id$observed)
KMfit <- survfit(surv ~ 1)
coxfit1 = survfit(coxph.fit1)
coxfit2 = survfit(coxph.fit2)
coxfit3 = survfit(coxph.fit3)
coxfit4 = survfit(coxph.fit4)



# Set up for ggplot
km <- rep("KM", length(KMfit$time))
km_df <- data.frame(KMfit$time,KMfit$surv,km)
names(km_df) <- c("Time","Surv","Model")

cox1 <- rep("Cox1",length(coxfit1$time))
cox_df1 <- data.frame(coxfit1$time,coxfit1$surv,cox1)
names(cox_df1) <- c("Time","Surv","Model")
cox2 <- rep("Cox2",length(coxfit2$time))
cox_df2 <- data.frame(coxfit2$time,coxfit2$surv,cox2)
names(cox_df2) <- c("Time","Surv","Model")
cox3 <- rep("Cox3",length(coxfit3$time))
cox_df3 <- data.frame(coxfit4$time,coxfit3$surv,cox3)
names(cox_df3) <- c("Time","Surv","Model")
cox4 <- rep("Cox4",length(coxfit4$time))
cox_df4 <- data.frame(coxfit4$time,coxfit4$surv,cox4)
names(cox_df4) <- c("Time","Surv","Model")

plot_df <- rbind(km_df,cox_df1,cox_df2, cox_df3, cox_df4)

p <- ggplot(plot_df, aes(x = Time, y = Surv, color = Model))
p + geom_line() + ggtitle("Comparison of Survival Curves") 




sim = predict(coxph.fit4, newdata=data_learning, type = "lp")
data_learning$pred = predict(coxph.fit4, newdata=data_learning, type = "lp")




