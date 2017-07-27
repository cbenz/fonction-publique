

################# Initialisation: 
# Packages
# Data loading
# Variables creation
# Tidy data for estimation


load_and_clean = function(data_path, dataname)
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
  
  return(list(data_id, data_max, data_min))
}  
