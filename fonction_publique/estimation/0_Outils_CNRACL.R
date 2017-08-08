################# Library of functions #######



## I. Managing data #####

load_and_clean = function(data_path, dataname)
# Input: inital data (name and path)
# Ouput: two datasets, with two definitions of duration in grade
{
  ## Chargement de la base
  filename = paste0(data_path, dataname)
  data_long = read.csv(filename)

  ## Variables creation ####

  # Format bolean                     
  to_bolean = c("indicat_ch_grade", "ambiguite", "right_censored", "left_censored", "exit_status")
  data_long[, to_bolean] <- sapply(data_long[, to_bolean], as.logical)
  
  # Corrections (to move to .py)
  #data_long$echelon[which(data_long$echelon == 55555)] = 12
  
  data_long$observed  = ifelse(data_long$right_censored == 1, 0, 1) 
  data_long$echelon_2011 = ave(data_long$echelon*(data_long$annee == 2011), data_long$ident, FUN = max)
  data_long$time_spent_in_grade_max  = data_long$annee - data_long$annee_min_entree_dans_grade + 1
  data_long$time_spent_in_grade_min  = data_long$annee - data_long$annee_max_entree_dans_grade + 1
    
  # Exit_status
  data_long$exit_status2 = ifelse(data_long$annee == data_long$last_y_observed_in_grade,1, 0)
  data_long$exit_status2[data_long$right_censored] = 0
  
  # Next grade
  data_next = data_long[which(data_long$annee == (data_long$last_y_observed_in_grade+1)), c('ident','c_cir')]
  data_next$next_grade2 = data_next$c_cir
  data_long = merge(data_long, data_next[,c("ident", "next_grade2")], by.x = "ident", all.x = T)
  data_long$next_grade = data_long$next_grade2
  data_long$next_grade2 = NULL
  
  data_long$next_year = ifelse(data_long$exit_status2 == 0, "no_exit", "exit_oth")
  data_long$next_year[which(data_long$exit_status2 == 1 & data_long$c_cir_2011 == "TTH1" & data_long$next_grade == "TTH2")] = "exit_next"
  data_long$next_year[which(data_long$exit_status2 == 1 & data_long$c_cir_2011 == "TTH2" & data_long$next_grade == "TTH3")] = "exit_next"
  data_long$next_year[which(data_long$exit_status2 == 1 & data_long$c_cir_2011 == "TTH3" & data_long$next_grade == "TTH4")] = "exit_next"
  
  data_long = data_long[order(data_long$ident,data_long$annee),]
  
  ## Institutional parameters (question: default value?)
  # Grade duration
  data_long$D_exam = 20
  data_long$D_exam[which(data_long$c_cir_2011 == "TTH1")] = 3
  data_long$D_choice = 20
  data_long$D_choice[which(data_long$c_cir_2011 == "TTH1")] = 10
  data_long$D_choice[which(data_long$c_cir_2011 == "TTH2")] = 6
  data_long$D_choice[which(data_long$c_cir_2011 == "TTH3")] = 5
  
  # Echelon (default = ?)
  data_long$E_exam = 12
  data_long$E_exam[which(data_long$c_cir_2011 == "TTH1")] = 4
  data_long$E_choice = 12
  data_long$E_choice[which(data_long$c_cir_2011 == "TTH1")] = 7
  data_long$E_choice[which(data_long$c_cir_2011 == "TTH2")] = 5
  data_long$E_choice[which(data_long$c_cir_2011 == "TTH3")] = 6
  
  # Next ib
  data_long$next_ib <-ave(data_long$ib, data_long$ident, FUN=shift1)
  data_long$var_ib  <-(data_long$next_ib - data_long$ib)/data_long$ib
  
  ## Data for estimations ####
  data_long = data_long[which(data_long$annee <= data_long$last_y_observed_in_grade),]
  
  # One line per year of observation (min and max)
  data_min = data_long[which(data_long$annee >= data_long$annee_min_entree_dans_grade),]
  data_min$time = data_min$time_spent_in_grade_max 
  data_max = data_long[which(data_long$annee >= data_long$annee_max_entree_dans_grade),]
  data_max$time = data_max$time_spent_in_grade_min
  
  ## Corrections (to move to .py)
  pb_ech = unique(data_max$ident[which(data_max$echelon == -1 & data_max$annee > 2010)])
  print(paste0(length(pb_ech),"  individus supprimes"))
  data_max = data_max[which(!is.element(data_max$ident, pb_ech)),]
  data_min = data_min[which(!is.element(data_min$ident, pb_ech)),]
  
  # One line per ident data
  data_id = data_long[!duplicated(data_long$ident),]
  data_id = data_id[which(!is.element(data_id$ident, pb_ech)),]
  
  return(list(data_max, data_min))
}  


# Variable creations 
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


### II. Simulation tools ####
predict_next_year <- function(p1,p2,p3)
{
  # random draw of next year situation based on predicted probabilities   
  n = sample(c("no_exit", "exit_next",  "exit_oth"), size = 1, prob = c(p1,p2,p3), replace = T)  
  return(n) 
}  

predict_next_grade <- function(next_situation, grade, exit_oth)
  # Predict next grade based on next situation and current situation.
  {
  # Default: same grade
  next_grade = as.character(grade)
  # Exit next: next
  next_grade[which(grade == "TTH1" & next_situation == "exit_next")] = "TTH2"
  next_grade[which(grade == "TTH2" & next_situation == "exit_next")] = "TTH3"
  next_grade[which(grade == "TTH3" & next_situation == "exit_next")] = "TTH4"
  # Exit oth: draw in probability
  for (g in c("TTH1", "TTH2", "TTH3", "TTH4"))
  {
  list1 = which(grade == g & next_situation == "exit_oth")
  data1 = data_exit_oth[which(data_exit_oth$c_cir == g),]
  table1 = table(data1$next_grade)/length(data1$next_grade)
  next_grade[list1]  = sample(names(table1), size = length(list1), prob = as.vector(table1), replace = T)  
  }
  return(next_grade) 
}  


extract_exit = function(data, exit_var, name)
# Fonction computing for each individual in data the year of exit and the grade of destination.
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
  colnames(data2)= paste0(colnames(data2), "_", name)
  return(data2)
}  



