




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
fig_path = paste0(git_path,"ecrits/modelisation_carriere/Figures/")
tab_path = paste0(git_path,"ecrits/modelisation_carriere/Tables/")


# Packages
#install.packages("OIsurv")
library(OIsurv)


# Chargement de la base
filename = paste0(data_path,"base_AT_clean_2007_2011/base_AT_clean.csv")
data_long = read.csv(filename)  

data_long$ind_exit_once = ave(data_long$exit_status, data_long$ident, FUN = max) 


# Mise au format data 1obs/indiv
data_id = data_long[,c("ident", "c_cir","generation","max_duration_in_grade","min_duration_in_grade","duration_in_grade_from_2011", "ind_exit_once",  "right_censoring")]
data_id = data_id[!duplicated(data_id$ident),]


### KM estimate ###
data_id$observed = ifelse(data_id$ind_exit_once == 1, 1, 0)
data_id$time_min = data_id$min_duration_in_grade + data_id$duration_in_grade_from_2011
data_id$time_max = data_id$max_duration_in_grade + data_id$duration_in_grade_from_2011


# All
my.surv <- Surv(data_id$time_max, data_id$observed)
my.fit <- survfit(my.surv ~ 1)
summary(my.fit)$surv     # returns the Kaplan-Meier estimate at each t_i
summary(my.fit)$time     # {t_i}
summary(my.fit)$n.risk   # {Y_i}
summary(my.fit)$n.event  # {d_i}
summary(my.fit)$std.err  # standard error of the K-M estimate at {t_i}
summary(my.fit)$lower    # lower pointwise estimates (alternatively, $upper)
str(my.fit)              # full summary of the my.fit object
str(summary(my.fit))     # full summary of the my.fit object

plot(my.fit, main="Kaplan-Meier estimate with 95% confidence bounds",
     xlab="time", ylab="survival function")


# TTH1
my.surv <- Surv(data_id$time_max[data_id$c_cir == "TTH1"], data_id$uncensored[data_id$c_cir == "TTH1"])
my.fit <- survfit(my.surv ~ 1)
plot(my.fit, main="KM for TTH1",
     xlab="time", ylab="survival function")
# TTH2
my.surv <- Surv(data_id$time_max[data_id$c_cir == "TTH2"], data_id$uncensored[data_id$c_cir == "TTH2"])
my.fit <- survfit(my.surv ~ 1)
plot(my.fit, main="KM for TTH2",
     xlab="time", ylab="survival function")
# TTH3
my.surv <- Surv(data_id$time_max[data_id$c_cir == "TTH3"], data_id$uncensored[data_id$c_cir == "TTH3"])
my.fit <- survfit(my.surv ~ 1)
plot(my.fit, main="KM for TTH3",
     xlab="time", ylab="survival function")
# TTH4
my.surv <- Surv(data_id$time_max[data_id$c_cir == "TTH4"], data_id$uncensored[data_id$c_cir == "TTH4"])
my.fit <- survfit(my.surv ~ 1)
plot(my.fit, main="KM for TTH4",
     xlab="time", ylab="survival function")



