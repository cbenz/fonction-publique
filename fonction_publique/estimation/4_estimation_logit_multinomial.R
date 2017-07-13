



################ Estimation by multinomial logit ################


source(paste0(wd, "0_work_on_data.R"))
datasets = load_and_clean(data_path, "data_ATT_2002_2015_with_filter_on_etat_at_exit_and_change_to_filter_on_etat_grade_corrected.csv")
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

data_est$I_bothC =  ifelse(data_est$I_echC ==1 &  data_est$I_gradeC == 1, 1, 0)

data_est$I_echE     = ifelse(data_est$echelon >= data_est$E_exam & data_est$c_cir_2011 == "TTH1", 1, 0) 
data_est$I_gradeE   = ifelse(data_est$time2 >= data_est$D_exam & data_est$c_cir_2011 == "TTH1", 1, 0) 
data_est$I_bothE    = ifelse(data_est$I_echE ==1 &  data_est$I_gradeE == 1, 1, 0) 

data_est$c_cir = factor(data_est$c_cir)

data_est$generation_group = factor(data_est$generation_group)
data_est$c_cir_2011 = factor(data_est$c_cir_2011)

data_est$age  = data_est$annee - data_est$generation
data_est$age2 = data_est$age*data_est$age

# Duration in grade
data_est$duration  = data_est$time
data_est$duration2 = data_est$time^2
# Duration in grade bef and after the threshold
data_est$duration_aft  = data_est$time*data_est$I_bothC
data_est$duration_aft2 = data_est$time^2*data_est$I_bothC
data_est$duration_bef  = data_est$time*(1-data_est$I_bothC)
data_est$duration_bef2 = data_est$time^2*(1-data_est$I_bothC)

# Unique threshold (first reached)
grade_modif_bis = which(data_est$c_cir_2011 == "TTH1")
data_est$I_unique_threshold = data_est$I_bothC
data_est$I_unique_threshold[grade_modif_bis] = data_est$I_bothE[grade_modif_bis]

data_est$duration_aft_unique_threshold  = data_est$time*data_est$I_unique_threshold
data_est$duration_aft_unique_threshold2 = data_est$time^2*data_est$I_unique_threshold

data_est$duration_bef_unique_threshold  = data_est$time*(1-data_est$I_unique_threshold)
data_est$duration_bef_unique_threshold2 = data_est$time^2*(1-data_est$I_unique_threshold)



#### I. Estimation ####
# 
# 
 varlist = c("ident", "annee", "sexe", "generation_group",  "an_aff", "c_cir_2011",
            "ib", "echelon", "time",
            "exit_status2", "next_grade","next_year",
            "I_unique_threshold", "duration","duration2",
            "duration_bef_unique_threshold", "duration_bef_unique_threshold2",
            "duration_aft_unique_threshold", "duration_aft_unique_threshold2")

years = 2011:2014
datam = data_est[which(is.element(data_est$annee, years)), varlist]
datam$c_cir_2011 = as.character(datam$c_cir_2011)

# estim = mlogit.data(datam, shape = "wide", choice = "next_year")
# 
# 
# mlog1 = mlogit(next_year ~ 0 | I_unique_threshold, data = estim, reflevel = "no_exit")
# mlog2 = mlogit(next_year ~ 0 | I_unique_threshold + c_cir_2011 + sexe + 
#                  duration_bef_unique_threshold +  duration_aft_unique_threshold, 
#                data = estim, reflevel = "no_exit")
# summary(mlog1)
# summary(mlog2)
# 
# ## Before/after
# l1 <- extract.mlogit(mlog1)
# l2 <- extract.mlogit(mlog2)
# 
# names = c("I_threshold", "Rank 2", "Rank 3", "Rank 4", "sexe = M", "duration_bef", "duration_bef2","duration_aft",
#           "duration_aft2", "duration", "duration2")
# 
# list_models    <- list(l1, l2)
# 
# 
# 
# print(texreg(list_models,
#              caption.above=F, 
#              float.pos = "!ht",
#              digit=3,
#              only.content= T,
#              stars = c(0.01, 0.05, 0.1),
#              #custom.coef.names=names,
#              #custom.coef.names=ror$ccn,  omit.coef=ror$oc, reorder.coef=ror$rc,
#              #omit.coef = omit_var,
#              booktabs=T), only.contents = T)
# 

# TODO: reorder coeffs


#### II Simulation ####


#### II.1 Predictions ####


list_id = unique(datam$ident)
list_learning = sample(list_id, ceiling(length(list_id)/2))
list_test = setdiff(list_id, list_learning)
data_learning = datam[which(is.element(datam$ident, list_learning)),]
data_test     = datam[which(is.element(datam$ident, list_test)),]


## 2011 ####
data_learning1 = data_learning[which(data_learning$annee == 2011),]
estim  = mlogit.data(data_learning1, shape = "wide", choice = "next_year")

data_test1     = data_test[which(data_test$annee == 2011),]
predict = mlogit.data(data_test1, shape = "wide", choice = "next_year")

mlog0 = mlogit(next_year ~ 0 | 1, data = estim, reflevel = "no_exit")
mlog1 = mlogit(next_year ~ 0 | c_cir_2011 + sexe + 
                 duration + duration2, data = estim, reflevel = "no_exit")
mlog2 = mlogit(next_year ~ 0 | I_unique_threshold + c_cir_2011 + sexe + 
                 duration_bef_unique_threshold +  duration_aft_unique_threshold, 
               data = estim, reflevel = "no_exit")

# Simulated exit

predict_next_year <- function(p1,p2,p3)
{
  n = sample(c("no_exit", "exit_next",  "exit_oth"), size = 1, prob = c(p1,p2,p3), replace = T)  
  return(n) 
}  


yhat0     <- predict(mlog0, predict, type = "response") 
yhat1     <- predict(mlog1, predict, type = "response") 
yhat2     <- predict(mlog2, predict, type = "response") 

data_test1$exit_hat0  <- mapply(predict_next_year, yhat0[,1], yhat0[,2], yhat0[,3])
data_test1$exit_hat1  <- mapply(predict_next_year, yhat1[,1], yhat1[,2], yhat1[,3])
data_test1$exit_hat2  <- mapply(predict_next_year, yhat2[,1], yhat2[,2], yhat2[,3])

table(data_learning1$next_year)/length(data_learning1$next_year)
table(data_test1$exit_hat0 )/length(data_test1$exit_hat0 )
table(data_test1$exit_hat2)/length(data_test1$exit_hat2 )



## Output for Python
data_test1$corps = "ATT"
data_test1$grade = data_test1$c_cir
data_test1$next_situation = NULL

data_test1$next_situation = data_test1$exit_hat0
data_simul_2011 = data_test1[, c("ident", "annee", "corps", "grade", "ib", "echelon", "next_situation")]
write.csv(data_simul_2011, file = paste0(save_data_path, "data_simul_2011_m0.csv"))

data_test1$next_situation = data_test1$exit_hat1
data_simul_2011 = data_test1[, c("ident", "annee", "corps", "grade", "ib", "echelon", "next_situation")]
write.csv(data_simul_2011, file = paste0(save_data_path, "data_simul_2011_m1.csv"))

data_test1$next_situation = data_test1$exit_hat2
data_simul_2011 = data_test1[, c("ident", "annee", "corps", "grade", "ib", "echelon", "next_situation")]
write.csv(data_simul_2011, file = paste0(save_data_path, "data_simul_2011_m2.csv"))


#### II.2 Adequacy analysis ####

###  II.2.1 2011-2012 only ###

## ROC analysis
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
  table_fit[6, m] = length(which(data_test1$exit_hat == 0 & data_test1$exit_status2 == 1))/length(which(data_test1$exit_status2 == 1))
  table_fit[7, m] = length(which(data_test1$exit_hat == 0 & data_test1$exit_status2 == 0))/length(which(data_test1$exit_status2 == 0))
  table_fit[8, m] = length(which(data_test1$exit_hat == 1 & data_test1$exit_status2 == 0))/length(which(data_test1$exit_status2 == 0))
}


colnames(table_fit) = c('Null model', 'Controls1', 'Controls2', 'Full model')
rownames(table_fit) = c('AIC', "BIC", "Prop of exit", "Diff pred. vs. obs", 
                        "(obs=1 + pred=1)/(obs=1)", "(obs=1 + pred=0)/(obs=1)",
                        "(obs=0 + pred=0)/(obs=0)", "(obs=0 + pred=1)/(obs=0)"
)

mdigit <- matrix(c(rep(0,(ncol(table_fit)+1)*2),rep(3,(ncol(table_fit)+1)*6)),nrow = nrow(table_fit), ncol=ncol(table_fit)+1, byrow=T)
print(xtable(table_fit,align="lcccc",nrow = nrow(table_fit), ncol=ncol(table_fit)+1, byrow=T, digits = mdigit),
      sanitize.text.function=identity,size="\\footnotesize", hline.after = c(0, 2, 4),
      only.contents=F, include.colnames = T)



## Fit by grade

table_by_grade = matrix(ncol = 4, nrow = 5)
for (m in 1:4)
{
  if (m == 1){data_test1$exit = data_test1$exit_status2}  
  if (m == 2){data_test1$exit = data_test1$exit_hat0}  
  if (m == 3){data_test1$exit = data_test1$exit_hat1}  
  if (m == 4){data_test1$exit = data_test1$exit_hat2}  
  if (m == 5){data_test1$exit = data_test1$exit_hat3}  
  
  # Predict/Observed
  table_by_grade[1, m] = mean(data_test1$exit)
  table_by_grade[2, m] = mean(data_test1$exit[which(data_test1$c_cir_2011 == "TTH1")])
  table_by_grade[3, m] = mean(data_test1$exit[which(data_test1$c_cir_2011 == "TTH2")])
  table_by_grade[4, m] = mean(data_test1$exit[which(data_test1$c_cir_2011 == "TTH3")])
  table_by_grade[5, m] = mean(data_test1$exit[which(data_test1$c_cir_2011 == "TTH4")])
}


colnames(table_by_grade) = c('Observed', 'Null model', 'Model 2', 'Model 3')
rownames(table_by_grade) = c("All", "TTH1", "TTH2", "TTH3", "TTH4")
print(xtable(table_by_grade,align="lcccc",nrow = nrow(table_by_grade), 
             ncol=ncol(table_fit_by_grade)+1, byrow=T, digits = 3),
      sanitize.text.function=identity,size="\\footnotesize",
      only.contents=F, include.colnames = T)



## Caracteristics of movers
data_test1$age = data_test1$annee - data_test1$generation
data_test1$femme =ifelse(data_test1$sexe == "F", 1, 0)

table_movers = matrix(ncol = 4, nrow = 11)
for (m in 1:4)
{
  if (m == 1){data_test1$exit = data_test1$exit_status2}  
  if (m == 2){data_test1$exit = data_test1$exit_hat0}  
  if (m == 3){data_test1$exit = data_test1$exit_hat1}  
  if (m == 4){data_test1$exit = data_test1$exit_hat2}  
  if (m == 5){data_test1$exit = data_test1$exit_hat3}  
  list = which(data_test1$exit == 1)
  table_movers[1,m] = mean(data_test1$exit)*100  
  table_movers[2,m] = mean(data_test1$age[list])
  table_movers[3,m] = mean(data_test1$femme[list])*100  
  table_movers[4:7,m] = as.numeric(table(data_test1$c_cir_2011[list]))/length(data_test1$c_cir_2011[list])*100
  table_movers[8,m] = mean(data_test1$ib[list])  
  table_movers[9:11,m] = as.numeric(quantile(data_test1$ib[list])[2:4])
}  

colnames(table_movers) = c('Observed', "Null model" , 'Controls1', 'Controls2', 'Full model')
rownames(table_movers) = c("Prop of exit", "Mean age", "\\% women", "\\% TTTH1", "\\% TTTH2", "\\% TTTH3", "\\% TTTH4",
                           "Mean ib", "Q1 ib", "Median ib", "Q3 ib")


print(xtable(table_movers,align="lcccc",nrow = nrow(table_movers), 
             ncol=ncol(table_movers)+1, byrow=T, digits = 0),
      sanitize.text.function=identity,size="\\footnotesize", hline.after = c(0, 2, 4),
      only.contents=F, include.colnames = T)


###  II.2.2 Survival analysis 2011-2014 ###





#### III. Nested logit  ####

### Hausman test IIA
data("TravelMode",package="AER")
TravelMode <- mlogit.data(TravelMode,choice="choice",shape="long",
                          alt.var="mode",chid.var="individual")
## Create a variable of income only for the air mode
TravelMode$avinc <- with(TravelMode,(mode=='air')*income)
## Estimate the model on all alternatives, with car as the base level
## like in Greene's book.
#x <- mlogit(choice~wait+gcost+avinc,TravelMode,reflevel="car")
x <- mlogit(choice~wait+gcost+avinc,TravelMode)
## Estimate the same model for ground modes only (the variable avinc
## must be dropped because it is 0 for every observation
g <- mlogit(choice~wait+gcost,TravelMode,reflevel="car",
            alt.subset=c("car","bus","train"))
## Compute the test
hmftest(x,g)