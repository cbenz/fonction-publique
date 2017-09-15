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


generate_data_sim <- function(data_path, path_utils, use = "min")
{
datasets = load_and_clean(data_path, dataname = "filter/data_ATT_2011_filtered_after_duration_var_added_new.csv")
if (use == "max"){data_obs = datasets[[1]]}
if (use == "min"){data_obs = datasets[[2]]}
data_obs  =  create_variables(data_obs) 
data_sim =  data_obs[which(data_obs$left_censored == F  & data_obs$annee == 2011),]
list_var = c("ident", "annee",  "sexe", "generation_group2", "c_cir_2011",
             "I_bothC", "I_bothE", "duration", "duration2", "duration3",
             "echelon", "time", "anciennete_echelon", "ib")
return(data_sim[, list_var])
}

generate_data_output <- function(data_path)
{
  filename = paste0(data_path, dataname)
  data_long = read.csv(filename)
  list_var = c("ident", "annee", "c_cir_2011", "grade","ib")
  output = data_long[which(data_long$annee <= 2015), list_var]
  return(output[, list_var])
}


increment_data_sim <- function(data_sim, data_results)
{
  datasets = load_and_clean(data_path, dataname = "filter/data_ATT_2011_filtered_after_duration_var_added_new.csv")
  if (use == "max"){data_obs = datasets[[1]]}
  if (use == "min"){data_obs = datasets[[2]]}
  data_obs  =  create_variables(data_obs) 
  data_sim =  data_obs[which(data_obs$left_censored == F  & data_obs$annee == 2011),]
  list_var = c("ident", "annee",  "sexe", "generation_group2", "c_cir_2011",
               "I_bothC", "I_bothE", "duration", "duration2", "duration3",
               "echelon", "time", "anciennete_echelon", "ib")
  return(data_sim[, list_var])
}

save_prediction_R <- function(data, annee, save_path, modelname)
{
  data$corps = "ATT"
  data$grade = data$c_cir
  data$next_situation = data$yhat
  data = data[, c("ident", "annee", "corps", "grade", "ib", "echelon", "next_situation")]
  filename = paste0(save_path, annee, "_data_simul_withR_",modelname,".csv")
  write.csv(data, file = filename)
  print(paste0("Data ", filename, " saved"))
}

launch_prediction_Py <- function(annee, python_file_path, modelname)
{
command ="python"
path2script= paste0(python_file_path, "simulation.py")
input_name = paste0(annee, "_data_simul_withR_",modelname,".csv")
output_name = paste0(annee, "_data_simul_withPy_",modelname,".csv")
input_arg = paste0("-i ", input_name)
output_arg = paste0("-o ", output_name)
args = c(annee, input_arg, output_arg)
# Add path to script as first arg
allArgs = c(path2script, args)
system2(command, args = allArgs)
}
  

launch_prediction_Py2 <- function(annee, modelname)
{
input_name = paste0(annee, "_data_simul_withR_",modelname,".csv")
output_name = paste0(annee, "_data_simul_withPy_",modelname,".csv")
input_arg = paste0(" -i ", input_name)
output_arg = paste0(" -o ", output_name)
debug = " -d"
args = paste0(input_arg, output_arg, debug)
command =  paste0('simulation',  args)
shell(command)
}


predict_next_year_MNL <- function(data_sim, model, modelname)
{
adhoc <- sample(c("no_exit",   "exit_next", "exit_oth"), nrow(data_sim), replace=TRUE, prob = c(0.2, 0.2, 0.6))
data_sim$next_year <-adhoc
data_predict_MNL <- mlogit.data(data_sim, shape = "wide", choice = "next_year")  
prob     <- predict(model, data_predict_MNL,type = "response") 
data_sim$yhat <- mapply(tirage_next_year_MNL, prob[,1], prob[,2], prob[,3])
return(data_sim)
}



for (m in 1:length(list_MNL))
  

for (annee in 2011:2014)
{
if (annee == 2011){data_sim = generate_data_sim(data_path, use = "min")}
# Prediction for MNL

{
model      = list_MNL[[m]]
modelname  =  paste0("MNL_", toString(m))  
pred =  predict_next_year_MNL(data_sim, model, modelname) 
save_prediction_R(data = pred, annee, save_data_simul_path, modelname)
launch_prediction_Py2(annee, modelname)

}

  
  
}
  
}


