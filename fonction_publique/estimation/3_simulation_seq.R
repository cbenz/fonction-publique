





##   MNM logit ##
list_models = list(mlog1, mlog2, mlog3)
for (m in 1:length(list_models))  
{
  
}  





####  I. Estimations ####

estimMNL  = mlogit.data(data_est, shape = "wide", choice = "next_year")
estimGLM  = data_est

##  I.1 MNM logit ##
mlog1 = mlogit(next_year ~ 0 | 1, 
               data = estimMNL, reflevel = "no_exit")
mlog2 = mlogit(next_year ~ 0 | sexe + generation_group2 + c_cir_2011 
               +  duration + duration2 + duration3, 
               data = estimMNL, reflevel = "no_exit")
mlog3 = mlogit(next_year ~ 0 | sexe + generation_group2 + c_cir_2011
               +  duration + duration2 + duration3 
               + I_bothC + I_bothE, 
               data = estimMNL, reflevel = "no_exit")

##  I.2 Model par grade ##
list1 = which(estimMNL$c_cir_2011 == "TTH1")
list2 = which(estimMNL$c_cir_2011 == "TTH2")
list3 = which(estimMNL$c_cir_2011 == "TTH3")

list4 = which(estimGLM$c_cir_2011 == "TTH4")
estimGLM$exit2 = ifelse(estimGLM$next_year == 'exit_oth',1, 0) 


mTTH1_1 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                   I_bothC + I_bothE + duration + duration2 + duration3, 
                 data = estimMNL[list1, ], reflevel = "no_exit")
mTTH2_1 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                   I_bothC +  duration + duration2 + duration3, 
                 data = estimMNL[list2, ], reflevel = "no_exit")
mTTH3_1 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                   I_bothC +  duration + duration2 + duration3, 
                 data = estimMNL[list3, ], reflevel = "no_exit")
mTTH4_1 = glm(exit2 ~  sexe + generation_group2 + 
                duration + duration2 + duration3, 
              data = estimGLM[list4, ], x=T, family=binomial("logit"))


##  I.3 Model sequentiel ##
estimGLM$exit = ifelse(estimGLM$next_year == 'exit_oth' | estimGLM$next_year =='exit_next', 1, 0)
estimGLM2 = estimGLM[which(estimGLM$exit == 1), ]
estimGLM2$exit_next = ifelse(estimGLM2$next_year =='exit_next', 1, 0)

step1_1 <- glm(exit ~  sexe + generation_group2 + c_cir_2011 + 
                 I_bothC + I_bothE + duration + duration2 + duration3, 
               data=estimGLM, x=T, family=binomial("logit"))
step2_1 <- glm(exit_next ~  sexe + generation_group2 + c_cir_2011 + 
                 I_bothC + I_bothE + duration + duration2 + duration3, 
               data=estimGLM2 , x=T, family=binomial("logit"))



####  II. Simulation ####



##  II.1 Prediction next_year ##



data_predict     <- data_sim

## TO DO: fonctions qui renvoit pour les M modèles un dataframe avec Nb ind nb de lignes et les variables 
# "ident", "next_situation", "next_grade"

##   MNM logit ##
list_models = list(mlog1, mlog2, mlog3)
for (m in 1:length(list_models))  
{
  model = list_models[[m]]
  prob     <- predict(model, data_predict_MNL,type = "response")   
  next_year_hat <-  paste0("next_year_hat_MNL_", toString(m))  
  data_sim[, next_year_hat] <- mapply(predict_next_year, prob[,1], prob[,2], prob[,3])
}  

##  Model par grade ##
list_models = list(mTTH1, mTTH2, mTTH3, mTTH4)
for (m in 1:length(list_models))  
{
  model = list_models[[m]]
  if (m < 4)
  {
    prob     <- predict(model, data_predict_MNL,type = "response")  
    next_year_hat <-  paste0("next_year_TTH", toString(m))  
    data_sim[, next_year_hat] <- mapply(predict_next_year, prob[,1], prob[,2], prob[,3])
  }
  if (m == 4)
  {
    prob     <- predict(model, data_predict, type = "response")  
    pred     <- as.numeric(mapply(tirage, prob))
    next_year_hat <-  paste0("next_year_TTH", toString(m))  
    data_sim[, next_year_hat] <- ifelse(pred == 1, "exit_oth", "no_exit")
  }
}  
data_sim$next_year_byG_1 = data_sim$next_year_TTH1
data_sim$next_year_byG_1[which(data_sim$c_cir_2011 == "TTH2")] =  data_sim$next_year_TTH2[which(data_sim$c_cir_2011 == "TTH2")] 
data_sim$next_year_byG_1[which(data_sim$c_cir_2011 == "TTH3")] =  data_sim$next_year_TTH3[which(data_sim$c_cir_2011 == "TTH3")] 
data_sim$next_year_byG_1[which(data_sim$c_cir_2011 == "TTH4")] =  data_sim$next_year_TTH4[which(data_sim$c_cir_2011 == "TTH4")] 


##  Modele séquentiel ##
prob1     <- predict(step1_1, data_predict, type = "response")  
pred1     <- as.numeric(mapply(tirage, prob1))
prob2     <- predict(step2_1, data_predict, type = "response")  
pred2     <- as.numeric(mapply(tirage, prob2))
data_sim$next_year_MS_1 <- ifelse(pred1 == 1, "exit", "no_exit")
data_sim$next_year_MS_1[which(pred1 == 1 & pred2 == 1)] <- "exit_next"
data_sim$next_year_MS_1[which(pred1 == 1 & pred2 == 0)] <- "exit_oth"



for (v in c("next_grade_situation", "next_year_hat_MNL_2","next_year_byG_1", "next_year_MS_1"))
{
  print(table(data_sim[,v]) )
}


## II.2 Simulation next grade  ##


list_all_models = c("next_year_hat_MNL_1", "next_year_hat_MNL_2","next_year_hat_MNL_3","next_year_byG_1", "next_year_MS_1")




## II.3 Save csv  ##
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

