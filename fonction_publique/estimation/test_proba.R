
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


source(paste0(wd, "0_Outils_CNRACL.R")) 
load(paste0(save_model_path, "mlog.rda"))
load(paste0(save_model_path, "m1_by_grade.rda"))


########## II. Compute probabilities in initial state #########

# Laod data
datasets = load_and_clean(data_path, dataname = "filter/data_ATT_2011_filtered_after_duration_var_added_new.csv")
data_max = datasets[[1]]
data_min = datasets[[2]]
data_est = data_min
data_obs = data_est[which(data_est$left_censored == F & data_est$annee == 2011 & data_est$generation < 1990),]
data_obs = data_obs[order(data_obs$ident),]
data_obs = create_variables(data_obs)  
data_obs$next_year = as.character(data_obs$next_grade_situation)
estim = mlogit.data(data_obs, shape = "wide", choice = "next_year")

data_proba = data_obs[,c("ident", "grade", "next_year", "duration", "echelon", "ib")]

# Observé
data_proba$no_exit_obs   = ifelse(data_proba$next_year == "no_exit",   1, 0)
data_proba$exit_next_obs = ifelse(data_proba$next_year == "exit_next", 1, 0)
data_proba$exit_oth_obs  = ifelse(data_proba$next_year == "exit_oth",  1, 0)
# Proba MNL
for (m in 1:length(list_MNL))
{
  prob <- as.data.frame(predict(list_MNL[[m]] , estim ,type = "response"))    
  names(prob) = paste0(names(prob), paste0("_MNL_",m))  
  data_proba = cbind(data_proba, prob)
}
# Proba model par grade
list_grade =  c("TTH1", "TTH2", "TTH3")
data_proba[, c("no_exit_byG",   "exit_next_byG", "exit_oth_byG")] = 0
for (g in 1:(length(list_by_grade)-1))
{
  list1 = which(estim$grade == list_grade[g])
  prob = predict(list_by_grade[[g]] , estim[list1,], type = "response")
  list2 = which(data_proba$grade == list_grade[g])
  data_proba[list2, c("no_exit_byG",   "exit_next_byG", "exit_oth_byG")] = prob
  stopifnot(length(setdiff(data_proba$ident[list2], estim$ident[list1])) == 0)
}
list = which(estim$grade == "TTH4")
prob = predict(list_by_grade[[4]], data_obs[list, ], type = "response")  
data_proba[list, "exit_oth_byG"] = prob
data_proba[list, "no_exit_byG"] = 1 - prob
# Model sequentiels
# TODO



### Sauvegarde de la base avec probas predites
save(data_proba, file = paste0(simul_path, "prob_pred.Rdata"))



#### II. Predicted probabilities ####

source(paste0(wd, "0_Outils_CNRACL.R")) 
load(paste0(simul_path, "prob_pred.Rdata"))

list_models = c("obs", "MNL_3", "byG")
model_names = c("Observé", "MNL", "Par grade")

plot_comp_predicted_prob_by_outcome = function(data_proba, list_models, model_names, outcome = "exit_next", xvariable = "duration")
{
  stopifnot(is.element(outcome, c("exit_next", "no_exit", "exit_oth")))  
  stopifnot(is.element(paste0("no_exit_", list_models), names(data_proba)))  
  stopifnot(length(list_models) == length(model_names)) 
  if(outcome == "exit_next"){data_proba = data_proba[which(data_proba$grade != "TTH4"),]}
  # Obs  
  for (m in 1:length(list_models))
  {
    var1 = c("exit_next", "no_exit", "exit_oth")
    var2 = paste0(c("exit_next_", "no_exit_", "exit_oth_"), list_models[m])
    data_proba[, var1] = data_proba[, var2]
    subdata = data_proba[, c(var1, "grade", xvariable)]
    subdata$xvariable = subdata[, xvariable]
    df <- aggregate(cbind(exit_next, no_exit , exit_oth ) ~ xvariable + grade, subdata, FUN= "mean" )
    df$mod = list_models[m]
    if (m == 1){means = df}
    if (m != 1){means = rbind(means, df)}
  }
  means$outcome = means[, outcome]
  ggplot(means, aes(x = xvariable, y = outcome, colour = mod)) + 
    geom_line( size = 1) + facet_grid(grade ~ ., scales = "free") + theme_bw() + 
    labs(x = xvariable) +labs(y = outcome) + labs(colour = "Modèles")
}

