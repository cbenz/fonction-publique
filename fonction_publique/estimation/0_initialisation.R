

################# Initialisation: 
# Packages
# Paths
# Data loading
# Variables creation
# Tidy data for estimation


rm(list = ls()); gc()

## Packages ####

#install.packages("OIsurv");install.packages("rms");install.packages("emuR");install.packages("RColorBrewer");install.packages("RcmdrPlugin");install.packages("flexsurv")
library(OIsurv)
library(rms)
library(emuR)
library(RColorBrewer)
library(RcmdrPlugin.survival)
library(flexsurv)


##  Paths ####

place = "ippS"
if (place == "ippS"){
  data_path = "M:/CNRACL/output/"
  git_path =  'U:/Projets/CNRACL/fonction-publique/fonction_publique/'
}
if (place == "ippL"){
  data_path = "M:/CNRACL/output/"
  git_path =  'C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/'
}
if (place == "mac"){
  data_path = "/Users/simonrabate/Desktop/data/CNRACL/"
  git_path =  '/Users/simonrabate/Desktop/IPP/CNRACL/fonction_publique/'
}
fig_path = paste0(git_path,"ecrits/Points AB/")
tab_path = paste0(git_path,"ecrits/modelisation_carriere/Tables/")

# Chargement de la base
filename = paste0(data_path,"clean_data_finalisation/data_ATT_2002_2015.csv")
#filename = paste0(data_path,"clean_data_finalisation/data_ATT_2002_2015_redef_var.csv")
data_long = read.csv(filename)


## Variable creation ####

# Corrections (to move to .py)
data_long$echelon[which(data_long$echelon == 55555)] = 12

# Exit_status
data_long$annee_exit = ave(data_long$annee, data_long$ident, FUN = max) 
data_long$exit_status2 = ifelse(data_long$annee == data_long$annee_exit,1, 0)
data_long$exit_status2[data_long$right_censored] = 0

# Format bolean                     
to_bolean = c("indicat_ch_grade", "ambiguite", "right_censored", "left_censored", "exit_status")
data_long[, to_bolean] <- sapply(data_long[, to_bolean], as.logical)

# Variables creation
data_long$observed  = ifelse(data_long$right_censored == 1, 0, 1) 
data_long$echelon_2011 = ave(data_long$echelon*(data_long$annee == 2011), data_long$ident, FUN = max)
data_long$time_spent_in_grade_max  = data_long$annee - data_long$annee_min_entree_dans_grade + 1
data_long$time_spent_in_grade_min  = data_long$annee - data_long$annee_max_entree_dans_grade + 1

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


## Data for estimations ####

# One line per year of observation (min and max)
data_min = data_long[which(data_long$annee >= data_long$annee_min_entree_dans_grade),]
data_min$time = data_min$time_spent_in_grade_max 
data_max = data_long[which(data_long$annee >= data_long$annee_max_entree_dans_grade),]
data_max$time = data_max$time_spent_in_grade_min

## Corrections (to move to .py)
pb_ech = unique(data_max$ident[which(data_max$echelon == -1)])
data_max = data_max[-which(is.element(data_max$ident, pb_ech)),]
data_min = data_min[-which(is.element(data_min$ident, pb_ech)),]

# One line per ident data
data_id = data_long[!duplicated(data_long$ident),]

