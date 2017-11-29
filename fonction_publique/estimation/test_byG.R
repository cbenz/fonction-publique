


### TEST TTH1


data_est = data_min
data_est = data_est[which(data_est$left_censored == F & data_est$annee == 2011 & data_est$generation < 1990),]
data_est = data_est[which(data_est$c_cir_2011 == "TTH1"),]
data_est = create_variables(data_est)  


test = data_est[which(data_est$c_cir_2011 == "TTH1"),]
table(test$exit_status2, test$dist_thresholdC)
table(test$T_condC, test$T_condE)


data_est$aft_seuil = ifelse(data_est$dist_thresholdC > 1, data_est$duration, 0)
data_est$aft_seuil2  =data_est$aft_seuil^2
data_est$mid_seuil  = ifelse(data_est$dist_thresholdC < 0 & data_est$dist_thresholdE>1, data_est$duration, 0)
data_est$mid_seuil2  =data_est$mid_seuil^2
data_est$bef_seuil = ifelse(data_est$dist_thresholdE < 0, data_est$duration, 0)
data_est$bef_seuil2  =data_est$bef_seuil^2

data_est$mid_seuil_bis  = ifelse(data_est$I_condC < 0 & data_est$I_condE>1, data_est$duration, 0)
data_est$mid_seuil_bis2  =data_est$mid_seuil^2


data_est$aft_seuil = ifelse(data_est$I_condC == 1, data_est$duration, 0)
data_est$aft_seuil2  =data_est$aft_seuil^2
data_est$mid_seuil  = ifelse(data_est$I_condC == 0 & data_est$I_condE == 1, data_est$duration, 0)
data_est$mid_seuil2  =data_est$mid_seuil^2
data_est$bef_seuil = ifelse(data_est$I_condE == 0, data_est$duration, 0)
data_est$bef_seuil2  =data_est$bef_seuil^2


# Drop outliers for duration
list_ident = data_est$ident[which(data_est$duration > 20)]
length(unique(list_ident))
data_est = data_est[which(!is.element(data_est$ident, list_ident)),]

data_est$next_year = as.character(data_est$next_grade_situation)

estim = mlogit.data(data_est, shape = "wide", choice = "next_year")

# TESTS TTH3
m1 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                   duration + duration2 , 
                 data = estim, reflevel = "no_exit")
m2 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                   I_condE + I_condC , 
                 data = estim, reflevel = "no_exit")
m3 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
              I_condE + I_condC +  duration + duration2, 
                 data = estim, reflevel = "no_exit")

m4 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
              T_condE + T_condC , 
            data = estim, reflevel = "no_exit")
m5 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
              T_condE + T_condC +  duration + duration2, 
            data = estim, reflevel = "no_exit")
m6 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
              I_condE + I_condC +  bef_seuil + mid_seuil + aft_seuil + bef_seuil2 + mid_seuil2 + aft_seuil2, 
            data = estim, reflevel = "no_exit")

listM = list(m1, m2, m3, m4, m5, m6)
namesM = c("Duration 1", "Seuil1", "Duration1 + seuil1", "Seuil 2", "Duration 2+ seuil2","Duration 3+ seuil2")
plot_comp_predicted_prob(data = data_est, data_estim = estim, list_models = listM, grade = "TTH1",
                         model_names = namesM, xvariable =  "duration")
plot_comp_predicted_prob(data = data_est, data_estim = estim, list_models = listM, grade = "TTH1",
                         model_names = namesM, xvariable =  "echelon")





### TEST TTH3


data_est = data_min
data_est = data_est[which(data_est$left_censored == F & data_est$annee == 2012 & data_est$generation < 1990),]
data_est = create_variables(data_est)  


data_est$aft_seuil = ifelse(data_est$dist_thresholdC > 1, data_est$duration, 0)
data_est$aft_seuil2  =data_est$aft_seuil^2
data_est$bef_seuil = ifelse(data_est$dist_thresholdC < 0, data_est$duration, 0)
data_est$bef_seuil2  =data_est$bef_seuil^2


test = data_est[which(data_est$c_cir_2011 == "TTH3"),]
table(test$exit_status2, test$dist_thresholdC)


# Drop outliers for duration
list_ident = data_est$ident[which(data_est$duration > 20)]
length(unique(list_ident))
data_est = data_est[which(!is.element(data_est$ident, list_ident)),]

data_est$next_year = as.character(data_est$next_grade_situation)

estim = mlogit.data(data_est, shape = "wide", choice = "next_year")

list3 = which(estim$c_cir_2011 == "TTH3")
# TESTS TTH3
m1 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                   duration + duration2 , 
                 data = estim[list3, ], reflevel = "no_exit")
m2 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                   I_condC +  duration_bis + duration2_bis , 
                 data = estim[list3, ], reflevel = "no_exit")
m3 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                   I_condC +  duration_befC_bis  + duration_befC2_bis +  duration_aftC_bis + duration_aftC2_bis , 
                 data = estim[list3, ], reflevel = "no_exit")

m4 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                   T_condC +  duration + duration2 , 
                 data = estim[list3, ], reflevel = "no_exit")
m5 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                   T_condC +  duration_bis + duration2_bis , 
                 data = estim[list3, ], reflevel = "no_exit")
m6 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                   T_condC +  bef_seuil + aft_seuil  , 
                 data = estim[list3, ], reflevel = "no_exit")



listM = list(m1, m2, m3, m4, m5, m6)
namesM = c("Duration 1", "Duration 2+ seuil1", "Duration 3+ seuil1","Duration 1+ seuil2","Duration 2+ seuil2","Duration 3+ seuil2")
plot_comp_predicted_prob(data = data_est, data_estim = estim, list_models = listM, grade = "TTH3",
                         model_names = namesM, xvariable =  "duration")
plot_comp_predicted_prob(data = data_est, data_estim = estim, list_models = listM, grade = "TTH3",
                         model_names = namesM, xvariable =  "echelon")
plot_comp_predicted_prob(data = data_est, data_estim = estim, list_models = listM, grade = "TTH3",
                         model_names = namesM, xvariable =  "dist_thresholdC")

