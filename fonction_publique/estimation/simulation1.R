


################ Simulation1 : exit rates  ################


## I. Simulation fonctions

draw_next <- function(p1,p2,p3)
{
  n = sample(c("no_exit", "exit_next",  "exit_oth"), size = 1, prob = c(p1,p2,p3), replace = T)  
  return(n) 
}  

extract_exit = function(data, exit_var)
  ## Fonction computing for each individual in data the year of exit and the grade of destination.
{
  data = data[, c("ident", "annee", exit_var)]
  data$exit_var = data[, exit_var]
  data$ind_exit       = ifelse(data$exit_var != "no_exit", 1, 0) 
  data$ind_exit_cum   = ave(data$ind_exit, data$ident, FUN = cumsum)
  data$ind_exit_cum2  = ave(data$ind_exit_cum, data$ident, FUN = cumsum)
  data$ind_exit_cum2  = ave(data$ind_exit_cum, data$ident, FUN = cumsum)
  data$ind_exit_tot   = ave(data$ind_exit, data$ident, FUN = sum)
  data$ind_first_exit  = ifelse(data$ind_exit_cum2 == 1, 1, 0) 
  data$year_exit = ave((data$ind_first_exit*data$annee), data$ident, FUN = max)
  data$year_exit[which(data$year_exit == 0)] = 2014
  data2 = data[which(data$annee == data$year_exit ),]
  data2$year_exit[which(data2$ind_exit_tot == 0)] = 9999
  data2 = data2[c("ident", "year_exit", "exit_var")]
  return(data2)
}  

simulation_exit <- function(list_models, data_obs, data_sim, data_predict)
  # Simulation output 1: comparaison des sorties de grade (date, destination)
  # Input: base de prédiction et modèles. 
  # Output: 2 matrices avec pour chaque individus l'année et la destination de sortie de grade.
  {

  # Ouput matrices
  exit_year  = matrix(nrow = length(list_models)+1, ncol = length(unique(data_sim$ident)))
  exit_route = matrix(nrow = length(list_models)+1, ncol = length(unique(data_sim$ident)))
  
  # Observed exits
  obs = extract_exit(data_obs, "next_year")
  exit_year[1,]  = obs$year_exit
  exit_route[1,]  = obs$exit_var
  
  # Predicted exits
  for (m in 1:length(list_models))  
  {
    model = list_models[[m]]
    prob     <- predict(model, data_predict,type = "response")   
    next_hat <-  paste0("next_hat_", toString(m))  
    data_sim[, next_hat] <- mapply(predict_next_year, prob[,1], prob[,2], prob[,3])
    sim = extract_exit(data = data_sim, next_hat)
    exit_year[(m+1), ]  = sim$year_exit
    exit_route[(m+1), ] = sim$exit_var
  }  
  
  return(list(exit_year, exit_route))
}
  

## II. Ouputs fonctions

# Hazards
hazard= function(exit_year, exit_route, sub_sample = "", type_exit = "all", name_graph = "", legend_labels = "",
                 save = F,  name_file = "hazard", ntypes = "", ncolors = "")
{
  # Init and checks
  if (length(sub_sample) == 1)    {sub_sample = 1:ncol(exit_year)}
  if (name_graph == ""){par(mar = c(4,4,2,2))} else {par(mar = c(4,4,1,1))}
  if (ncolors == "")       {ncolors = colorRampPalette(c("black", "grey"))(nrow(exit_year))}
  if (ntypes == "")        {ntypes = rep(1, nrow(exit_year))}
  if (legend_labels == "") {legend_labels = c("Obs", paste0("Sim_",1:(nrow(exit_year)-1)))}
  if (!is.element(type_exit, c("all", "exit_next", "exit_oth"))){print("wrong exit type"); return()}
  if (save == T & name_file == ""){print("No file name"); return()}
  
  years = 2011:2014
  haz  = matrix(ncol = length(years), nrow = nrow(exit_year))  
  list = sub_sample
  n = length(list)

  
  for (m in 1:nrow(exit_year))
  {
    for (y in 1:length(years))
    {
  # All
    if (type_exit == "all"){
    haz[m, y] =  length(which(exit_year[m, list] == years[y]))/length(which(exit_year[m, list] >= years[y]))
    }
    else{
    haz[m, y] =  length(which(exit_year[m, list] == years[y] & exit_route[m,list] == type_exit))/
                    length(which(exit_year[m, list] >= (years[y])))
    }
    }
  }
  
  # Plot
  if (save){pdf(paste0(fig_path, name_file,".pdf"))}
  years = 2012:2015
  colors = c("black", "darkcyan")
  limits = c(min(haz),max(haz)+0.05*max(haz))
  plot(years,rep(NA,length(years)),ylim=limits, ylab="Hazard rate",xlab="Année")
  title(name_graph)
  for (m in (1:nrow(exit_year))){lines(years, haz[m,], lwd = 3 , col =  ncolors[m], lty = ntypes[m])}
  legend("topright", legend = legend_labels, col = ncolors, lty = ntypes, lwd = 3)
  if (save){dev.off()}
}


## Main
simulation_diagnosis = function(list_models, data_obs, data_pred 
                                , legend_labels = ""
                                , save = F,  ntypes = "", ncolors = ""
                                , hazards = T
                                , by_grade = T)
  {
  #Predictions
  pred = simulation_exit(list_models, data_obs, data_sim, data_predict)  
  exit_year =  pred[[1]]
  exit_route =  pred[[2]]
  # Ouputs
  if (hazards)
  {
    hazard(exit_year, exit_route, sub_sample = "", type_exit = "all", name_graph = "All", legend_labels = "",
                       save = F,  name_file = "hazard_all", ntypes = "", ncolors = "")  
    hazard(exit_year, exit_route, sub_sample = "", type_exit = "exit_next", name_graph = "Next", legend_labels = legend_labels,
             save = save,  name_file = "hazard_next", ntypes = ntypes, ncolors = ncolors)  
    hazard(exit_year, exit_route, sub_sample = "", type_exit = "exit_oth", name_graph = "Oth", legend_labels = legend_labels,
           save = save,  name_file = "hazard_oth", ntypes = ntypes, ncolors = ncolors)  
  
    if (by_grade)
    {
    for (grade in c("TTH1", "TTH2", "TTH3", "TTH4"))
    {
    subsample =  which(data_obs$c_cir_2011[which(data_obs$annee == 2011)] == grade) 
    hazard(exit_year, exit_route, sub_sample = subsample, type_exit = "all", name_graph = paste0("All, ", grade), legend_labels = "",
           save = F,  name_file = "hazard_all", ntypes = "", ncolors = "")  
    hazard(exit_year, exit_route, sub_sample = subsample, type_exit = "exit_next", name_graph = paste0("Next, ", grade), legend_labels = legend_labels,
           save = save,  name_file = "hazard_next", ntypes = ntypes, ncolors = ncolors)  
    hazard(exit_year, exit_route,  sub_sample = subsample, type_exit = "exit_oth", name_graph = paste0("Oth, ", grade), legend_labels = legend_labels,
           save = save,  name_file = "hazard_oth", ntypes = ntypes, ncolors = ncolors)  
    }
    }
  }
 }


simulation_diagnosis (list_models, data_obs, data_pred 
                                , legend_labels = ""
                                , save = F,  ntypes = "", ncolors = ""
                                , hazards = T
                                , by_grade = T)