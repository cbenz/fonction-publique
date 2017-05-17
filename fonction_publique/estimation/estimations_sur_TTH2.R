




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
#install.packages("OIsurv");install.packages("rms");install.packages("emuR");install.packages("RColorBrewer")
library(OIsurv)
library(rms)
library(emuR)
library(RColorBrewer)

# Chargement de la base
filename = paste0(data_path,"base_AT_clean_2007_2011/base_AT_clean.csv")
data_long = read.csv(filename)  

data_long$ind_exit_once = ave(data_long$exit_status, data_long$ident, FUN = max) 

# Mise au format data 1obs/indiv
data_id = data_long[,c("ident", "c_cir","generation","max_duration_in_grade","min_duration_in_grade","duration_in_grade_from_2011", "ind_exit_once",  "right_censoring")]
data_id = data_id[!duplicated(data_id$ident),]

data_id$observed = ifelse(data_id$ind_exit_once == 1, 1, 0)
data_id$time_min = data_id$min_duration_in_grade + data_id$duration_in_grade_from_2011
data_id$time_max = data_id$max_duration_in_grade + data_id$duration_in_grade_from_2011



# Data grade TTH3, Adjoint technique principal de 2ème classe, 5 ans de services eff. sont nécessaires pour passer
# au grade suivant
data_TTH3 <- data_id[data_id$c_cir == 'TTH3',]


## I. Descriptive statistics ####


## I.1 KM estimation ####

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
my.surv <- Surv(data_id$time_max[data_id$c_cir == "TTH1"], data_id$observed[data_id$c_cir == "TTH1"])
my.fit <- survfit(my.surv ~ 1)
plot(my.fit, main="KM for TTH1",
     xlab="time", ylab="survival function")
# TTH2
my.surv <- Surv(data_id$time_max[data_id$c_cir == "TTH2"], data_id$observed[data_id$c_cir == "TTH2"])
my.fit <- survfit(my.surv ~ 1)
plot(my.fit, main="KM for TTH2",
     xlab="time", ylab="survival function")
# TTH3
my.surv <- Surv(data_id$time_max[data_id$c_cir == "TTH3"], data_id$observed[data_id$c_cir == "TTH3"])
my.fit <- survfit(my.surv ~ 1)
plot(my.fit, main="KM for TTH3",
     xlab="time", ylab="survival function")
# TTH4
my.surv <- Surv(data_id$time_max[data_id$c_cir == "TTH4"], data_id$observed[data_id$c_cir == "TTH4"])
my.fit <- survfit(my.surv ~ 1)
plot(my.fit, main="KM for TTH4",
     xlab="time", ylab="survival function")


## II. Estimation ####


attach(data_TTH3)

## II.1 Exponential/Weibull ####


## Exponential
srFit_exp <- survreg(Surv(time_max, observed) ~ generation, dist = "exponential")
summary(srFit_exp)

srFit_exp <- survreg(Surv(time_max, observed) ~ generation, dist = "loglogistic")
summary(srFit_exp)


## Weibull 
srFit_weibull <- survreg(Surv(time_max, observed) ~ generation, dist = "weibull")
summary(srFit_weibull)

a <- 1/srFit_weibull$scale 
b <- exp( coef(srFit_weibull) )
y2 <- b * ( -log( 1-runif(1000) ) ) ^(1/a)
plot(sort(y2), main="Conditional Weibull Hazard",
     xlab="time", ylab="Hazard")


## Comparison


## II.3  Cox PH with time-dependent variable ####

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

