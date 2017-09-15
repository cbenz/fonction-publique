




################ Estimation by logit ################


#### 0. Initialisation ####

# Main data
source(paste0(wd, "0_Outils_CNRACL.R"))
<<<<<<< HEAD
datasets = load_and_clean(data_path, "/filter/data_ATT_2011_filtered_after_duration_var_added_new.csv")
=======
<<<<<<< HEAD
datasets = load_and_clean(data_path, "/filter/data_ATT_2011_filtered_after_duration_var_added_new.csv")
=======
datasets = load_and_clean(data_path, "data_ATT_2002_2015_with_filter_on_etat_at_exit_and_change_to_filter_on_etat_grade_corrected.csv")
>>>>>>> 93b186717408d8840b39b31bb775fb54e8e7bdd5
>>>>>>> 2a5c043f2827b0f0932cbfac30b9f067667ea687
data_max = datasets[[1]]
data_min = datasets[[2]]

# Sample selection
<<<<<<< HEAD
data_est = data_min[which(data_min$annee  == 2011),]
=======
<<<<<<< HEAD
data_est = data_min[which(data_min$annee  == 2011),]
=======
data_est =  data_min[which(data_min$annee  == 2011),]
>>>>>>> 93b186717408d8840b39b31bb775fb54e8e7bdd5
>>>>>>> 2a5c043f2827b0f0932cbfac30b9f067667ea687
data_est = create_variables(data_est)  


#### I. Estimation ####



## I.1 Binomial ####

model1 <- glm(exit_status2 ~  I_unique_threshold,
              data=data_est,x=T,family=binomial("logit"))

model2 <- glm(exit_status2 ~ I_unique_threshold +  c_cir_2011 + sexe,
              data=data_est,x=T,family=binomial("logit"))

model3 <- glm(exit_status2 ~ I_unique_threshold  + c_cir_2011 + sexe + 
                duration_aft_unique_threshold + duration_bef_unique_threshold,
               data=data_est,x=T,family=binomial("logit"))

model4 <- glm(exit_status2 ~ I_unique_threshold  + c_cir_2011 + sexe + 
                duration_aft_unique_threshold +  duration_aft_unique_threshold2 + 
                duration_bef_unique_threshold +  duration_bef_unique_threshold2,
              data=data_est,x=T,family=binomial("logit"))

model5 <- glm(exit_status2 ~ c_cir_2011 + sexe + 
                duration + duration2,
              data=data_est,x=T,family=binomial("logit"))

me1 <- logitmfx(exit_status2 ~  I_unique_threshold,
                data=data_est, atmean = F)

me2 <- logitmfx(exit_status2 ~ I_unique_threshold +  c_cir_2011 + sexe,
                data=data_est, atmean = F)

me3 <- logitmfx(exit_status2 ~ I_unique_threshold  + c_cir_2011 + sexe + 
                  duration_bef_unique_threshold + duration_aft_unique_threshold,
                data=data_est, atmean = F)

me4 <- logitmfx(exit_status2 ~ I_unique_threshold  + c_cir_2011 + sexe + 
                duration_bef_unique_threshold +  duration_bef_unique_threshold2+
                duration_aft_unique_threshold +  duration_aft_unique_threshold2,
                data=data_est, atmean = F)

me5 <- logitmfx(exit_status2 ~  c_cir_2011 + sexe + 
                  duration + duration2,
                data=data_est, atmean = F)

## Before/after
l1 <- extract.glm2(model1, include.aic = T, include.bic=F, include.loglik = F, include.deviance = F)
l2 <- extract.glm2(model2, include.aic = T, include.bic=F, include.loglik = F, include.deviance = F)
l3 <- extract.glm2(model3, include.aic = T, include.bic=F, include.loglik = F, include.deviance = F)
l4 <- extract.glm2(model4, include.aic = T, include.bic=F, include.loglik = F, include.deviance = F)
l5 <- extract.glm2(model4, include.aic = T, include.bic=F, include.loglik = F, include.deviance = F)

lme1 <- extract(me1, include.aic = T, include.bic=F, include.loglik = F, include.deviance = F)
lme2 <- extract(me2, include.aic = T, include.bic=F, include.loglik = F, include.deviance = F)
lme3 <- extract(me3, include.aic = T, include.bic=F, include.loglik = F, include.deviance = F)
lme4 <- extract(me4, include.aic = T, include.bic=F, include.loglik = F, include.deviance = F)
lme5 <- extract(me5, include.aic = T, include.bic=F, include.loglik = F, include.deviance = F)



names = c("I_threshold", "Rank 2", "Rank 3", "Rank 4", "sexe = M", "duration_bef", "duration_bef2","duration_aft",
          "duration_aft2", "duration", "duration2")

list_models    <- list(l1, l2, l3, l4, l5)
list_models_me <- list(lme2, lme4, lme5)

print(texreg(list_models_me,
             caption.above=F, 
             float.pos = "!ht",
             digit=3,
             only.content= T,
             stars = c(0.01, 0.05, 0.1),
             custom.coef.names=names,
             #custom.coef.names=ror$ccn,  omit.coef=ror$oc, reorder.coef=ror$rc,
             #omit.coef = omit_var,
             booktabs=T), only.contents = T)


## I.2 Multinomial ####

