




######## Estimation survival ########

## I. KM estimation ####


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




## II. Parametric estimation ####


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

plot_comp_fit_param(data_id)
plot_comp_fit_param(data_id, grade = "TTH1")
plot_comp_fit_param(data_id, grade = "TTH2")
plot_comp_fit_param(data_id, grade = "TTH3")
plot_comp_fit_param(data_id, grade = "TTH4")



## III  Cox PH ####

## III.1  Cox PH with time-fixed variable ####
attach(data_TTH3)

my.surv   <- Surv(time_max, observed)
coxph.fit1 <- coxph(my.surv ~ sexe + as.factor(generation_group), method="breslow") #sexe +
coxph.fit3 <- coxph(my.surv ~ sexe +  as.factor(generation_group), method="efron")

plot(survfit(coxph.fit1), ylim=c(0, 1), xlab="Year",ylab="Proportion in grade")

detach(data_TTH3)


## III.2  Cox PH with time-dependent variables ####

## III.2.1  0/1 Treatment ####

data = data_max[which(data_max$left_censored == F & data_max$c_cir_2011 == "TTH3"),]
data = data_max[which(data_max$left_censored == F & data_max$echelon != - 1),]
data = data_min[which(data_min$left_censored == F),]

# Start/stop
data$start = data$time - 1
data$stop = data$time 

# Distance variables
data$I_echelon = ifelse(data$echelon >= data$E_choice, 1, 0) 
data$I_grade = ifelse(data$time >= data$D_choice, 1, 0) 
data$dist_an_aff = data$annee - data$an_aff +1 
data$I_grade[which(data$c_cir_2011 == "TTH2")] = ifelse(data$dist_an_aff[which(data$c_cir_2011 == "TTH2")] >= data$D_choice[which(data$c_cir_2011 == "TTH2")], 1, 0) 
data$I_both = ifelse(data$time >= data$D_choice & data$echelon >= data$E_choice, 1, 0) 

data$c_cir = factor(data$c_cir)

coxph.fit1 = coxph(Surv(start, stop, exit_status2) ~  sexe + factor(generation_group) + c_cir_2011 +  I_echelon,
                   data=data)
coxph.fit2 = coxph(Surv(start, stop, exit_status2) ~  sexe + factor(generation_group) + c_cir_2011 +  I_grade,
                   data=data)
coxph.fit3 = coxph(Surv(start, stop, exit_status2) ~  sexe + factor(generation_group) + c_cir_2011 + I_grade + I_echelon + I_grade*I_echelon,
                   data=data)
coxph.fit4 = coxph(Surv(start, stop, exit_status2) ~  sexe + factor(generation_group) + c_cir_2011 +  I_grade*I_echelon,
                   data=data)

## III.2.2  Distance to threshold dummies (Chetty) #######

data = data_max[which(data_max$left_censored == F & data_max$c_cir_2011 == "TTH3"),]
data = data_max[which(data_max$left_censored == F),]

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

for(d in unique(data$dist_grade)) {
  if (d<=-4){data[paste("dist_grade_m4",sep="")] <- ifelse(data$dist_grade<=-4,1,0)}
  else if  (d>=4){data[paste("dist_grade_p4",sep="")] <- ifelse(data$dist_grade>=4,1,0)}
  else if  (d<0){data[paste("dist_grade_m",abs(d),sep="")] <- ifelse(data$dist_grade==d,1,0)}
  else if  (d==0){data[paste("dist_grade_",d,sep="")] <- ifelse(data$dist_grade==d,1,0)}
  else if  (d>0){data[paste("dist_grade_p",d,sep="")] <- ifelse(data$dist_grade==d,1,0)}
}




list_id = data$ident
list_learning = sample(list_id, ceiling(length(list_id)/2))
list_test = setdiff(list_id, list_learning)
data_learning = data[which(is.element(data$ident, list_learning)),]
data_test     = data[which(is.element(data$ident, list_test)),]


coxph.fit1 = coxph(Surv(start, stop, exit_status2) ~  sexe + generation_group + c_cir_2011 +
                     dist_echelon_m3 + dist_echelon_m2 + dist_echelon_m1 + dist_echelon_0 + 
                     dist_echelon_p1 + dist_echelon_p2 + dist_echelon_p3 + dist_echelon_p4,
                   data=data_learning)

coxph.fit2 = coxph(Surv(start, stop, exit_status2) ~  sexe + generation_group +
                     dist_grade_m3 + dist_grade_m2 + dist_grade_m1 + dist_grade_0 + 
                     dist_grade_p1 + dist_grade_p2 + dist_grade_p3 + dist_grade_p4,
                   data=data_learning)


data_test$pred = predict(coxph.fit2, newdata=data_test, type = "lp")



## IV  Parametric estimation with time-dependent variables ####


data = data_min[which(data_min$left_censored == F),]
data_id = data_id[which(data_id$left_censored == F),]
data_id$time = data_id$duree_max




srFit_exp <- flexsurvreg(Surv(start, stop, exit_status2) ~  sexe + generation_group +
                           dist_grade_m3 + dist_grade_m2 + dist_grade_m1 + dist_grade_0 + 
                           dist_grade_p1 + dist_grade_p2 + dist_grade_p3 + dist_grade_p4,
                         data=data_learning, dist = "exponential")





######## V. Simulations ########


# Start/stop
data$start = data$time - 1
data$stop = data$time 

# Distance variables
data$I_echelon = ifelse(data$echelon >= data$E_choice, 1, 0) 
data$I_grade = ifelse(data$time >= data$D_choice, 1, 0) 
data$dist_an_aff = data$annee - data$an_aff +1 
data$I_grade[which(data$c_cir_2011 == "TTH2")] = ifelse(data$dist_an_aff[which(data$c_cir_2011 == "TTH2")] >= data$D_choice[which(data$c_cir_2011 == "TTH2")], 1, 0) 
data$I_both = ifelse(data$time >= data$D_choice & data$echelon >= data$E_choice, 1, 0) 
data$c_cir = factor(data$c_cir)


list_id = data$ident
list_learning = sample(list_id, ceiling(length(list_id)/2))
list_test = setdiff(list_id, list_learning)
data_learning = data[which(is.element(data$ident, list_learning)),]
data_test     = data[which(is.element(data$ident, list_test)),]


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




