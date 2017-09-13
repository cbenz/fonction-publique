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



####  I. Estimations ####

estimMNL  = mlogit.data(data_est, shape = "wide", choice = "next_year")
estimGLM  = data_est

##  I.1 MNM logit ##
mlog1 = mlogit(next_year ~ 0 | sexe + generation_group2 + c_cir_2011 
               +  duration + duration2 + duration3, 
               data = estim, reflevel = "no_exit")
mlog2 = mlogit(next_year ~ 0 | sexe + generation_group2 + c_cir_2011
                 +  duration + duration2 + duration3 
                 + I_bothC + I_bothE, 
               data = estim, reflevel = "no_exit")

##  I.2 Model par grade ##
list1 = which(estimMNL$c_cir_2011 == "TTH1")
list2 = which(estimMNL$c_cir_2011 == "TTH2")
list3 = which(estimMNL$c_cir_2011 == "TTH3")

list4 = which(estimGLM$c_cir_2011 == "TTH4")
estimGLM$exit2 = ifelse(estimGLM$next_year == 'exit_oth',1, 0) 


mTTH1 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                 I_bothC + I_bothE + duration + duration2 + duration3, 
               data = estimMNL[list1, ], reflevel = "no_exit")
mTTH2 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                 I_bothC +  duration + duration2 + duration3, 
               data = estimMNL[list2, ], reflevel = "no_exit")
mTTH3 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                 I_bothC +  duration + duration2 + duration3, 
               data = estimMNL[list3, ], reflevel = "no_exit")
mTTH4 = glm(exit2 ~  sexe + generation_group2 + 
              duration + duration2 + duration3, 
            data = estimGLM[list4, ], x=T, family=binomial("logit"))


##  I.3 Model sequentiel ##
estimGLM$exit = ifelse(estimGLM$next_year == 'exit_oth' | estimGLM$next_year =='exit_next', 1, 0)
estimGLM2 = estimGLM[which(estimGLM$exit == 1), ]
estimGLM2$exit_next = ifelse(estimGLM2$next_year =='exit_next', 1, 0)

step1 <- glm(exit ~  sexe + generation_group2 + c_cir_2011 + 
               I_bothC + I_bothE + duration + duration2 + duration3, 
             data=estimGLM, x=T, family=binomial("logit"))
step2 <- glm(exit_next ~  sexe + generation_group2 + c_cir_2011 + 
               I_bothC + I_bothE + duration + duration2 + duration3, 
             data=estimGLM2 , x=T, family=binomial("logit"))



####  II. Simulation ####

adhoc <- sample(c("no_exit",   "exit_next", "exit_oth"), nrow(data_sim), replace=TRUE, prob = c(0.2, 0.2, 0.6))
data_sim$next_year <-adhoc
data_predict <- mlogit.data(data_sim, shape = "wide", choice = "next_year")



## TO DO: fonctions qui renvoit pour les M modèles un dataframe avec Nb ind nb de lignes et les variables 
# "ident", "next_situation", "next_grade"

##  I.1 MNM logit ##
list_models = list(mlog1, mlog2)
for (m in 1:length(list_models))  
{
model = list_models[[m]]
prob     <- predict(model, data_predict,type = "response")   
next_year_hat <-  paste0("next_year_hat_MNL_", toString(m))  
data_sim[, next_year_hat] <- mapply(predict_next_year, prob[,1], prob[,2], prob[,3])
}  

##  I.2 Model par grade ##
list_models = list(mTTH1, mTTH2, mTTH3, mTTH4)
for (m in 1:length(list_models))  
{
  model = list_models[[m]]
  prob     <- predict(model, data_predict,type = "response")  
  if (m == 1)
  {
    next_year_hat <-  paste0("next_year_hat_MNL_", toString(m))  
    data_sim[, next_year_hat] <- mapply(predict_next_year, prob[,1], prob[,2], prob[,3])
  }
}  


## Simulation outputs
data_sim2 = data_sim[which(data_sim$annee == 2011), ]
data_exit_oth = data_min[which(data_min$next_year == "exit_oth"), c("c_cir", "next_grade")]
data_sim2$corps = "ATT"
data_sim2$grade = data_sim2$c_cir
data_sim2$ib = data_sim2$ib_2011
data_sim2$next_situation = NULL

for (m in 1:length(list_models))  
{
data_sim2$next_situation = data_sim2[, paste0("next_year_hat_", toString(m))  ]
data_sim2$next_grade = predict_next_grade(data_sim2$next_situation, data_sim2$c_cir_2011, data_exit_oth)
data_simul_2011 = data_sim2[, c("ident", "annee", "corps", "grade", "ib", "echelon", "next_situation", "next_grade")]
write.csv(data_simul_2011, file = paste0(save_data_path, "data_simul_2011_bis_m",m,".csv"))
}  

