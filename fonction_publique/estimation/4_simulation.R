




################ Simulation with multinomial logit ################


# Simulation of trajectories based on estimation of the model. 
# Two types of simulations: 
#     i) Simulation of grade exit (2011 --> 2015)
#     ii)  Simulation of next ib (2011 --> 2012)



#### 0. Initialisation ####


### Load data ###

# Observed data for estimation
source(paste0(wd, "0_work_on_data.R"))
datasets = load_and_clean(data_path, "data_ATT_2002_2015_with_filter_on_etat_at_exit_and_change_to_filter_on_etat_grade_corrected.csv")
data_id = datasets[[1]]
data_max = datasets[[2]]
data_min = datasets[[3]]

data_est = data_min[which(data_min$annee == 2011),]

# Counterfactual data for simulation + merge for relevant variables
echelon_cf = read.csv("M:/CNRACL/output/simulation_counterfactual_echelon/results_annuels.csv")
data1 = echelon_cf[which(echelon_cf$annee >= 2011 & echelon_cf$annee < 2015), c("ident", "annee", "echelon", "c_cir")]

data_min$I_2011 = ifelse(data_min$annee == 2011, 1, 0)
data_min$ib_2011 = ave(data_min$I_2011*data_min$ib, data_min$ident, FUN = max)
data2 = data_min[which(data_min$annee == 2011), 
                 c("ident", "time", "sexe", "an_aff", "left_censored", "generation_group", "c_cir_2011", "ib_2011",
                   "D_exam", "D_choice", "E_exam", "E_choice")]
data_sim = merge(data1, data2, by = "ident")
data_sim$time_2011 = data_sim$time 
data_sim$time =  data_sim$time  + data_sim$annee - 2011

data_sim = data_sim[order(data_sim$ident,data_sim$annee),]


#### Variable creations ####

create_variables <- function(data)
{
  data$dist_an_aff = data$annee - data$an_aff +1 
  grade_modif = which(data$c_cir_2011 == "TTH1" | data$c_cir_2011 == "TTH2")
  data$time2 = data$time
  data$time2[grade_modif] = data$dist_an_aff[grade_modif] 
  data$I_echC = ifelse(data$echelon >= data$E_choice, 1, 0) 
  data$I_gradeC   = ifelse(data$time2 >= data$D_choice, 1, 0) 
  data$I_gradeC   = ifelse(data$time2 >= data$D_choice, 1, 0) 
  data$I_bothC =  ifelse(data$I_echC ==1 &  data$I_gradeC == 1, 1, 0) 
  data$I_echE     = ifelse(data$echelon >= data$E_exam & data$c_cir_2011 == "TTH1", 1, 0) 
  data$I_gradeE   = ifelse(data$time2 >= data$D_exam & data$c_cir_2011 == "TTH1", 1, 0) 
  data$I_bothE    = ifelse(data$I_echE ==1 &  data$I_gradeE == 1, 1, 0) 
  data$c_cir = factor(data$c_cir)
  
  data$duration = data$time
  data$duration2 = data$time^2 
  
  data$duration  = data$time
  data$duration2 = data$time^2
  
  data$duration_aft  = data$time*data$I_bothC
  data$duration_aft2 = data$time^2*data$I_bothC
  
  data$duration_bef  = data$time*(1-data$I_bothC)
  data$duration_bef2 = data$time^2*(1-data$I_bothC)
  
  data$generation_group = factor(data$generation_group)
  data$c_cir_2011 = factor(data$c_cir_2011)
  
  # Unique threshold (first reached)
  grade_modif_bis = which(data$c_cir_2011 == "TTH1")
  data$I_unique_threshold = data$I_bothC
  data$I_unique_threshold[grade_modif_bis] = data$I_bothE[grade_modif_bis]
  
  data$duration_aft_unique_threshold  = data$time*data$I_unique_threshold
  data$duration_aft_unique_threshold2 = data$time^2*data$I_unique_threshold
  
  data$duration_bef_unique_threshold  = data$time*(1-data$I_unique_threshold)
  data$duration_bef_unique_threshold2 = data$time^2*(1-data$I_unique_threshold)
  
  
  return(data)
}
  
data_est = create_variables(data_est)  
data_sim = create_variables(data_sim)  


data_obs =  data_min[which(data_min$left_censored == F & data_min$annee <= 2014),]
data_est =  data_est[which(data_est$left_censored == F),]
data_sim =  data_sim[which(data_sim$left_censored == F  & data_sim$annee <= 2014),]


adhoc <- sample(c("no_exit",   "exit_next", "exit_oth") ,nrow(data_sim),replace=TRUE, prob = c(0.2, 0.2, 0.6))
data_sim$next_year <-adhoc
data_predict  = mlogit.data(data_sim, shape = "wide", choice = "next_year")

# Multinomial
estim  = mlogit.data(data_est, shape = "wide", choice = "next_year")


mlog0 = mlogit(next_year ~ 0 | 1, data = estim, reflevel = "no_exit")
mlog1 = mlogit(next_year ~ 0 | c_cir_2011 + sexe 
               + duration + duration2 
               , data = estim, reflevel = "no_exit")
mlog2 = mlogit(next_year ~ 0 | I_unique_threshold + c_cir_2011 + sexe  
               +  duration_bef_unique_threshold +  duration_aft_unique_threshold 
               , data = estim, reflevel = "no_exit")

summary(mlog1)
summary(mlog2)



### Functions ###
predict_next_year <- function(p1,p2,p3)
{
n = sample(c("no_exit", "exit_next",  "exit_oth"), size = 1, prob = c(p1,p2,p3), replace = T)  
return(n) 
}  

extract_exit = function(data, exit_var)
{
  data = data[, c("ident", "annee", exit_var)]
  
  data$exit_var = data[, exit_var]
  data$ind_exit      = ifelse(data$exit_var != "no_exit", 1, 0) 
  data$ind_exit_cum  = ave(data$ind_exit, data$ident, FUN = cumsum)
  data$ind_exit_cum2  = ave(data$ind_exit_cum, data$ident, FUN = cumsum)
  data$ind_exit_cum2  = ave(data$ind_exit_cum, data$ident, FUN = cumsum)
  data$ind_exit_tot   = ave(data$ind_exit, data$ident, FUN = sum)
  ### PB  
  data$ind_first_exit  = ifelse(data$ind_exit_cum2 == 1, 1, 0) 
  data$year_exit = ave((data$ind_first_exit*data$annee), data$ident, FUN = max)
  data$year_exit[which(data$year_exit == 0)] = 2014
  data2 = data[which(data$annee == data$year_exit ),]
  data2$year_exit[which(data2$ind_exit_tot == 0)] = 9999
  data2 = data[c("ident", "year_exit", "exit_var")]
  return(data2)
}  





list_models = list(mlog0, mlog1, mlog2)


simulation_output1 <- function(list_models, data_obs, data_predict, save = F){
# Simulation output 1: comparaison des sorties de grade (date, destination)
# Input: base de prédiction et modèles. 
# Output: 1) Hazard rates, 2) Tables fit (par grade, ib, année, etc)

  # Checks:
  if (nrow(data_obs)!=nrow(data_predict)){print("Problem"): stop()}
  
  ## I. Predictions 
  
  # Predicted status in next year 
  for (m in 1:length(list_models))  
  {
  model = list_models[[m]]
  prob     <- predict(model, data_predict,type = "response")   
  next_hat <-  paste0("next_hat_", toString(m))  
  data_sim[, next_hat] <- mapply(predict_next_year, prob[,1], prob[,2], prob[,3])
  }  
  
  # Save year of exit and exit routes
  exit_year  = matrix(nrow = length(list_models)+1, ncol = length(unique(data_sim$ident)))
  exit_route = matrix(nrow = length(list_models)+1, ncol = length(unique(data_sim$ident)))

  # Obs
  obs = extract_exit(data_obs, "next_year")
  exit_year[1,]  = obs$year_exit
  exit_route[1,]  = obs$exit_vars
  
  # Sim
  for (d in 0:2){
    exit_var = paste0("next_hat", d)  
    print(exit_var)
    sim = extract_exit(data = data_sim, exit_var)
    exit_year_pred[(d+1), ]  = sim$year_exit
    exit_route_pred[(d+1), ] = sim$exit_var
  }
  
  ## II. Ouputs

  
  

  
}  
    

simulation_output2 <- function(list_models, data_predict, save = F){
  # Simulation output 2: comparaison des ib prédits et observés.
  # Input: base de prédiction et modèles. 
  # Output: 1) Distributions 2) Tables fit (par grade, ib, année, etc)
  # TODO: gérer interface Python 
  
} 



#### I. Estimation ####




#### II. Predictions ####


## II.1 Predicted exit ##


# Simulated exit (all years)




#### II.2 Prediction ib ####

data_sim2  <- data_sim[which(data_sim$annee == 2011),]
data_predict2  = mlogit.data(data_sim2, shape = "wide", choice = "next_year")


yhat0     <- predict(mlog0, data_predict2, type = "response") 
yhat1     <- predict(mlog1, data_predict2, type = "response") 
yhat2     <- predict(mlog2, data_predict2, type = "response") 

data_sim2$next_hat0  <- mapply(predict_next_year, yhat0[,1], yhat0[,2], yhat0[,3])
data_sim2$next_hat1  <- mapply(predict_next_year, yhat1[,1], yhat1[,2], yhat1[,3])
data_sim2$next_hat2  <- mapply(predict_next_year, yhat2[,1], yhat2[,2], yhat2[,3])


mean(data_sim2$ib[which(data_sim2$next_year == "no_exit")])
mean(data_sim2$ib[which(data_sim2$next_hat0 == "no_exit")])
mean(data_sim2$ib[which(data_sim2$next_hat1 == "no_exit")])
mean(data_sim2$ib[which(data_sim2$next_hat2 == "no_exit")])
mean(data_sim2$ib[which(data_sim2$next_year == "no_exit")])
mean(data_sim2$ib[which(data_sim2$next_hat0 == "no_exit")])
mean(data_sim2$ib[which(data_sim2$next_hat1 == "no_exit")])
mean(data_sim2$ib[which(data_sim2$next_hat2 == "no_exit")])

table(data_sim2$next_hat0)
table(data_sim2$next_hat1)
table(data_sim2$next_hat2)

data_sim2$corps = "ATT"
data_sim2$grade = data_sim2$c_cir
data_sim2$next_situation = NULL

data_sim2$next_situation = data_sim2$next_hat0
data_simul_2011 = data_sim2[, c("ident", "annee", "corps", "grade", "ib", "echelon", "next_situation")]
write.csv(data_simul_2011, file = paste0(save_data_path, "data_simul_2011_m0.csv"))

data_sim2$next_situation = data_sim2$next_hat1
data_simul_2011 = data_sim2[, c("ident", "annee", "corps", "grade", "ib", "echelon", "next_situation")]
write.csv(data_simul_2011, file = paste0(save_data_path, "data_simul_2011_m1.csv"))

data_sim2$next_situation = data_sim2$next_hat2
data_simul_2011 = data_sim2[, c("ident", "annee", "corps", "grade", "ib", "echelon", "next_situation")]
write.csv(data_simul_2011, file = paste0(save_data_path, "data_simul_2011_m2.csv"))



### III. Comparison predicted vs. observed ###



### III.1 Survival 2011-2014 ####

## Survival curve
survival= function(sample, type_exit = "all", save = F, name = "")
{
  years = 2011:2015
surv  = matrix(ncol = 5, nrow = 4)  
list = sample
for (y in 1:length(years))
{
  n = length(list)
  surv[1, y] = (n - length(which(exit_year_obs[list] < years[y])))/n
  surv[2, y] = (n - length(which(exit_year_pred[1, list]  < years[y])))/n
  surv[3, y] = (n - length(which(exit_year_pred[2, list]  < years[y])))/n
  surv[4, y] = (n - length(which(exit_year_pred[3, list]  < years[y])))/n  
}
# Plot

colors = c("black", "darkcyan")
limits = range(surv)
plot(years,rep(NA,length(years)),ylim=limits, ylab="Survie dans le grade",xlab="Année")
title(name)
lines(years, surv[1,], col =  colors[1], lwd = 3, lty =1)
lines(years, surv[2,], col =  colors[2], lwd = 3, lty = 2)
lines(years, surv[3,], col =  colors[2], lwd = 4, lty = 3)
lines(years, surv[4,], col =  colors[2], lwd = 4, lty =1)
legend("topright", legend = c("Obs", "m0", "m1", "m2"), col = c(colors[1], rep(colors[2], 3)), lty = c(1,2,3,1), lwd = 3)
}

datai= data_sim[which(data_sim$annee == 2011),]
survival(sample = 1:ncol(exit_year_pred), type_exit = "all", save = F, name = "Tous")

par(mfrow=c(2,2))
survival(sample = which(datai$c_cir_2011 == "TTH1"), type_exit = "all", save = F, name = "TTH1")
survival(sample = which(datai$c_cir_2011 == "TTH2"), type_exit = "all", save = F, name = "TTH2")
survival(sample = which(datai$c_cir_2011 == "TTH3"), type_exit = "all", save = F, name = "TTH3")
survival(sample = which(datai$c_cir_2011 == "TTH4"), type_exit = "all", save = F, name = "TTH4")



hazard= function(sample, type_exit = "all", save = F, name = "")
{
  haz  = matrix(ncol = 4, nrow = 4)  
  list = sample
  years = 2011:2014
  
  if (!is.element(type_exit, c("all", "exit_next", "exit_oth"))){print("wrong exit type"); return()}
  
  # All
  if (type_exit == "all")
  {
  for (y in 1:length(years))
  {
    n = length(list)
    haz[1, y] =  length(which(exit_year_obs[list] == years[y]))/length(which(exit_year_obs[list] >= years[y]))
    haz[2, y] =  length(which(exit_year_pred[1, list] == years[y]))/length(which(exit_year_pred[1, list] >= years[y]))
    haz[3, y] =  length(which(exit_year_pred[2, list] == years[y]))/length(which(exit_year_pred[2, list]  >= years[y]))
    haz[4, y] =  length(which(exit_year_pred[3, list] == years[y]))/length(which(exit_year_pred[3, list ] >= years[y]))
  }
  }
  else{
    for (y in 1:length(years))
    {
      n = length(list)
      haz[1, y] =  length(which(exit_year_obs[list] == years[y] & exit_route_obs[list] == type_exit))/length(which(exit_year_obs[list] >= (years[y])))
      haz[2, y] =  length(which(exit_year_pred[1, list] == years[y] & exit_route_pred[1,list] == type_exit))/length(which(exit_year_pred[1, list] >= years[y])) 
      haz[3, y] =  length(which(exit_year_pred[2, list] == years[y] & exit_route_pred[2,list] == type_exit))/length(which(exit_year_pred[2, list] >= years[y]))
      haz[4, y] =  length(which(exit_year_pred[3, list] == years[y] & exit_route_pred[3,list] == type_exit))/length(which(exit_year_pred[3, list] >= years[y]))
    }
    
  }
  
  # Plot
  years = 2012:2015
  colors = c("black", "darkcyan")
  limits = range(haz)
  plot(years,rep(NA,length(years)),ylim=limits, ylab="Hazard rate",xlab="Année")
  title(name)
  lines(years, haz[1,], col =  colors[1], lwd = 3, lty =1)
  lines(years, haz[2,], col =  colors[2], lwd = 3, lty = 2)
  lines(years, haz[3,], col =  colors[2], lwd = 4, lty = 3)
  lines(years, haz[4,], col =  colors[2], lwd = 4, lty =1)
}


hazard(sample = 1:ncol(exit_year_pred), type_exit = "all",       save = F, name = "All")
hazard(sample = 1:ncol(exit_year_pred), type_exit = "exit_next", save = F, name = "Next grade")
hazard(sample = 1:ncol(exit_year_pred), type_exit = "exit_oth",  save = F, name = "Exit corps")


hazard(sample = which(datai$c_cir == "TTH1"), type_exit = "all",       save = F, name = "All exits, TTH1")
hazard(sample = which(datai$c_cir == "TTH1"), type_exit = "exit_next", save = F, name = "Next grade, TTH1")
hazard(sample = which(datai$c_cir == "TTH1"), type_exit = "exit_oth",  save = F, name = "Next grade, TTH1")


hazard(sample = which(datai$c_cir == "TTH2"), type_exit = "all",       save = F, name = "All exits, TTH2")
hazard(sample = which(datai$c_cir == "TTH3"), type_exit = "all",       save = F, name = "All exits, TTH3")
hazard(sample = which(datai$c_cir == "TTH4"), type_exit = "all",       save = F, name = "All exits, TTH4")


hazard(sample = which(datai$c_cir == "TTH2"), type_exit = "exit_next", save = F, name = "Next grade")
hazard(sample = which(datai$c_cir == "TTH3"), type_exit = "exit_next", save = F, name = "Next grade")
hazard(sample = which(datai$c_cir == "TTH4"), type_exit = "exit_next", save = F, name = "Next grade")

hazard(sample = 1:ncol(exit_year_pred), type_exit = "exit_oth",  save = F, name = "All")






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

table_by_grade = matrix(ncol = 5, nrow = 5)
for (m in 1:5)
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

colnames(table_by_grade) = c('Observed', 'Null model', 'Controls1', 'Controls2', 'Full model')
rownames(table_by_grade) = c("All", "TTH1", "TTH2", "TTH3", "TTH4")
print(xtable(table_by_grade,align="lccccc",nrow = nrow(table_by_grade), 
             ncol=ncol(table_fit_by_grade)+1, byrow=T, digits = 3),
      sanitize.text.function=identity,size="\\footnotesize",
      only.contents=F, include.colnames = T)



## Caracteristics of movers
data_test1$age = data_test1$annee - data_test1$generation
data_test1$femme =ifelse(data_test1$sexe == "F", 1, 0)

table_movers = matrix(ncol = 5, nrow = 11)
for (m in 1:5)
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


print(xtable(table_movers,align="lccccc",nrow = nrow(table_movers), 
             ncol=ncol(table_movers)+1, byrow=T, digits = 0),
      sanitize.text.function=identity,size="\\footnotesize", hline.after = c(0, 2, 4),
      only.contents=F, include.colnames = T)


### III.2 IB 2012 : obs. vs. sim ####


