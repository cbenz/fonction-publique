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


generate_data_sim <- function(data_path, use = "min")
{
datasets = load_and_clean(data_path, dataname = "filter/data_ATT_2011_filtered_after_duration_var_added_new.csv")
if (use == "max"){data = datasets[[1]]}
if (use == "min"){data = datasets[[2]]}
list_var = c("ident", "annee",  "sexe", "c_cir_2011", "generation", "an_aff",
             "E_exam", "E_choice", "D_exam", "D_choice",
             "time", "anciennete_dans_echelon", "echelon", "ib")
data = data[which(data$left_censored == F  & data$annee == 2011),
                    list_var ]
data_sim  =  create_variables(data) 
return(data_sim)
}

generate_data_output <- function(data_path)
{
  filename = paste0(data_path, dataname)
  data_long = read.csv(filename)
  list_var = c("ident", "annee", "c_cir_2011", "grade","ib")
  output = data_long[which(data_long$annee <= 2015), list_var]
  return(output[, list_var])
}


save_prediction_R <- function(data, annee, save_path, modelname)
{
  data$corps = "ATT"
  data$grade = data$c_cir
  data$next_situation = data$yhat
  data = data[, c("ident", "annee", "corps", "grade", "ib", "echelon", "anciennete_dans_echelon", "next_situation")]
  filename = paste0(save_path, annee, "_data_simul_withR_",modelname,".csv")
  write.csv(data, file = filename)
  print(paste0("Data ", filename, " saved"))
}


launch_prediction_Py <- function(annee, modelname, debug = F)
{
input_name = paste0(annee, "_data_simul_withR_",modelname,".csv")
output_name = paste0(annee, "_data_simul_withPy_",modelname,".csv")
input_arg = paste0(" -i ", input_name)
output_arg = paste0(" -o ", output_name)
d = ifelse(debug, " -d", "")
args = paste0(input_arg, output_arg, d)
command =  paste0('simulation',  args)
shell(command)
}


load_simul_py <- function(annee, modelname)
{
  filename = paste0(simul_path, paste0(annee, "_data_simul_withPy_",modelname,".csv"))
  simul = read.csv(filename)  
  return(simul)
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


increment_data_sim <- function(data_sim, simul_py)
{
  if (length(data_sim$ident != length(simul_py$ident)))
  {
    print(paste0("Il y a ",length(data_sim$ident)," individus dans la base_sim et ", length(data_sim$ident)," dans simul"))
    list_id = unique(simul_py$ident)
    data_sim = data_sim[which(is.element(data_sim$ident, list_id))]
  }
  # CHECK
  data_sim = cbind(data_sim, simul_py[, c("next_annee", "next_grade", "next_echelon", "next_ib", 
                                           "next_situation", "next_anciennete_dans_echelon")])
  
  # Merge
  list_var_kept1 = c("ident",  "sexe", "generation", "an_aff", "c_cir_2011", "grade",
               "E_exam", "E_choice", "D_exam", "D_choice", "time")
  list_var_kept2 = c("annee", "grade", "echelon", "ib", "anciennete_dans_echelon", "next_situation")
  data_sim = cbind(data_sim[,list_var_kept], simul_py[, var2])
  
  # Increment time
  data_sim$time[which(data_sim$next_situation == "no_exit")] = data_sim$time[which(data_sim$next_situation == "no_exit")] + 1
  data_sim$time[which(data_sim$next_situation != "no_exit")] = 1
  
  return(data_sim)
}


for (m in 1:length(list_MNL))
{
for (annee in 2011:2014)
{
if (annee == 2011){data_sim = generate_data_sim(data_path, use = "min")}
model      = list_MNL[[m]]
modelname  =  paste0("MNL_", toString(m))  
# Prediction of next_situation from estimated model 
pred =  predict_next_year_MNL(data_sim, model, modelname) 
save_prediction_R(data = pred, annee, simul_path, modelname)
# Prediction of next_ib using simulation.py
launch_prediction_Py(annee, modelname)
# Load and save results
simul_py = load_simul_py(annee, modelname)
#save_results_simul(output, simul_py, modelname)
# Incrementing data_sim for next year
data_sim = increment_data_sim(data_sim, simul_py)
}
}

