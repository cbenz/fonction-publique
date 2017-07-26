################ Simulation with multinomial logit ################


# Simulation of trajectories based on estimation of the model. 
# Two types of simulations: 
#     i) Simulation of grade exit (2011 --> 2015) 
#     ii)  Simulation of next ib (2011 --> 2012)

# Program: 
# 0.  Initialisation: data loading and variable creations
# I.  Estimation: estimation of the models for predictions
# II. Simulation: from estimates, creating the two outputs for simulation diagnosis. 



#### 0. Initialisation ####

# Main data
source(paste0(wd, "0_Outils_CNRACL.R"))
datasets = load_and_clean(data_path, "data_ATT_2002_2015_with_filter_on_etat_at_exit_and_change_to_filter_on_etat_grade_corrected.csv")
data_max = datasets[[1]]
data_min = datasets[[2]]

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

# Sample selection
data_obs =  data_min[which(data_min$left_censored == F & data_min$annee >= 2011 & data_min$annee <= 2014),]
data_est =  data_obs[which(data_obs$annee  == 2011),]
data_sim =  data_sim[which(data_sim$left_censored == F  & data_sim$annee <= 2014),]

# Variables creation
data_est = create_variables(data_est)  
data_sim = create_variables(data_sim)  



## I. Estimation ####
estim  = mlogit.data(data_est, shape = "wide", choice = "next_year")

mlog1 = mlogit(next_year ~ 0 | 1 
               , data = estim, reflevel = "no_exit")

mlog2 = mlogit(next_year ~ 0 | I_unique_threshold + c_cir_2011 + sexe  
               +  duration + duration2
               , data = estim, reflevel = "no_exit")

mlog3 = mlogit(next_year ~ 0 | I_unique_threshold + c_cir_2011 + sexe  
               +  duration_bef_unique_threshold +  duration_aft_unique_threshold 
               , data = estim, reflevel = "no_exit")

summary(mlog1)
summary(mlog2)
summary(mlog3)

## II. Simulation

adhoc <- sample(c("no_exit",   "exit_next", "exit_oth") ,nrow(data_sim),replace=TRUE, prob = c(0.2, 0.2, 0.6))
data_sim$next_year <-adhoc
data_predict  = mlogit.data(data_sim, shape = "wide", choice = "next_year")

list_models = list(mlog1, mlog2, mlog3)


for (m in 1:length(list_models))  
{
  model = list_models[[m]]
  prob     <- predict(model, data_predict,type = "response")   
  next_hat <-  paste0("next_hat_", toString(m))  
  data_sim[, next_hat] <- mapply(predict_next_year, prob[,1], prob[,2], prob[,3])
}  


## Simulation outputs

# 1. Data with exit observed and predicted + invidual beetween 2011 and 2014
var = c("ident", "generation_group", "c_cir_2011", "sexe", "an_aff")
data1  <- data_obs[which(data_sim$annee == 2011), var]
obs = extract_exit(data_obs, "next_year", "obs")
data1 = cbind(data1, obs[,c(2,3)])
for (m in 1:length(list_models))  
{
  var <- paste0("next_hat_", toString(m))  
  name <-  paste0("pred_", toString(m))  
  pred = extract_exit(data_sim, var, name)
  data1 = cbind(data1, pred[,c(2,3)])
}  
save(data1,  file = paste0(save_data_path, "data_simul1.Rdata"))

# 2.  Data with prediction for imputing next 
data_sim2 = data_sim[which(data_sim$annee == 2011), ]

data_sim2$corps = "ATT"
data_sim2$grade = data_sim2$c_cir
data_sim2$next_situation = NULL

for (m in 1:length(list_models))  
{
  data_sim2$next_situation = data_sim[, paste0("next_hat_", toString(m))  ]
  data_simul_2011 = data_sim2[, c("ident", "annee", "corps", "grade", "ib", "echelon", "next_situation")]
  write.csv(data_simul_2011, file = paste0(save_data_path, "data_simul_2011_m",m,".csv"))
}  

