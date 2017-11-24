



################ Estimation by multinomial logit ################



# Main data
source(paste0(wd, "0_Outils_CNRACL.R"))
datasets = load_and_clean(data_path, dataname = "filter/data_ATT_2011_filtered_after_duration_var_added_new.csv")
data_max = datasets[[1]]
data_min = datasets[[2]]

# Sample selection
data_est = data_min
data_est = data_est[which(data_est$left_censored == F & data_est$annee == 2011 & data_est$generation < 1990),]
data_est = create_variables(data_est)  


#### I. Simple logit ####

data_est$next_year = as.character(data_est$next_grade_situation)
data_est$duration2 = data_est$time^2 
data_est$duration3 = data_est$time^3 

estim = mlogit.data(data_est, shape = "wide", choice = "next_year")

mlog0 = mlogit(next_year ~ 0 | 1, data = estim, reflevel = "no_exit")
mlog1 = mlogit(next_year ~ 0 | sexe + generation_group2, data = estim, reflevel = "no_exit")
mlog1 = mlogit(next_year ~ 0 | sexe + generation_group2 + grade + I_echC + I_echE, data = estim, reflevel = "no_exit")
mlog2 = mlogit(next_year ~ 0 | sexe + generation_group2 + grade, data = estim, reflevel = "no_exit")
mlog3 = mlogit(next_year ~ 0 | sexe + generation_group2 + grade + duration + duration2 + duration3, data = estim, reflevel = "no_exit")
mlog4 = mlogit(next_year ~ 0 | sexe + generation_group2 + grade + I_bothC, data = estim, reflevel = "no_exit")
mlog5 = mlogit(next_year ~ 0 | sexe + generation_group2 + grade + I_bothC + I_bothE, 
                data = estim, reflevel = "no_exit")
mlog6 = mlogit(next_year ~ 0 | sexe + generation_group2 + grade + 
               I_bothC + I_bothE + duration + duration2 + duration3, 
               data = estim, reflevel = "no_exit")


list_MNL = list(mlog0, mlog1, mlog3, mlog6)
save(list_MNL, file = paste0(save_model_path, "mlog.rda"))


# bundle up some models
m1 = extract.mlogit2(mlog1, include.aic =  T )
m2 = extract.mlogit2(mlog2, include.aic =  T )
m3 = extract.mlogit2(mlog3, include.aic =  T )
m4 = extract.mlogit2(mlog4, include.aic =  T )
m5 = extract.mlogit2(mlog5, include.aic =  T )
m6 = extract.mlogit2(mlog6, include.aic =  T )

model.list <- list(m1, m2, m3, m4, m5, m6)

name.map <- list("exit_next:(intercept)"       = "exit_next: constante",
                 "exit_next:sexeM"             = "exit_next: Homme",  
                 "exit_next:generation_group22"= "exit_next: Generation 70s", 
                 "exit_next:generation_group23"= "exit_next: Generation 80s", 
                 "exit_next:gradeTTH2"    = "exit_next: TTH2",  
                 "exit_next:gradeTTH3"    = "exit_next: TTH3", 
                 "exit_next:gradeTTH4"    = "exit_next: TTH4",
                 "exit_next:I_bothC"            = "exit_next: Conditions choix remplies",
                 "exit_next:I_bothE"            = "exit_next: Conditions exam remplies",
                 "exit_next:I_echC"            = "exit_next: Conditions echelon choix remplies",
                 "exit_next:I_echE"            = "exit_next: Conditions echelon exam remplies",
                 "exit_oth:(intercept)"        = "exit_oth: constante",              
                 "exit_oth:sexeM"              = "exit_oth: Homme",
                 "exit_oth:generation_group22" = "exit_oth: Generation 70s",
                 "exit_oth:generation_group23" = "exit_oth: Generation 80s",
                 "exit_oth:gradeTTH2"     = "exit_oth: TTH2",
                 "exit_oth:gradeTTH3"     = "exit_oth: TTH3",
                 "exit_oth:gradeTTH4"     = "exit_oth: TTH4",
                 "exit_oth:I_bothC"            = "exit_oth: Conditions choix remplies",
                 "exit_oth:I_bothE"            = "exit_oth: Conditions exam remplies",
                 "exit_oth:I_echC"            = "exit_oth: Conditions echelon choix remplies",
                 "exit_oth:I_echE"            = "exit_oth: Conditions echelon exam remplies")


oldnames <- all.varnames.dammit(model.list) 
ror <- build.ror(oldnames, name.map)


print(texreg2(model.list,
             caption.above=F,
             float.pos = "!ht",
             digit=3,
             stars = c(0.01, 0.05, 0.1),
             custom.coef.names=ror$ccn,   reorder.coef=ror$rc,  omit.coef=ror$oc,
             booktabs=T))


#### II. One logit by Grade ####


list1 = which(estim$grade == "TTH1")
list2 = which(estim$grade == "TTH2")
list3 = which(estim$grade == "TTH3")
list4 = which(data_est$grade == "TTH4")

data_est$exit2 = ifelse(data_est$next_year == 'exit_oth',1, 0) 

m1_all = mlogit(next_year ~ 0 | sexe + generation_group2 + grade + 
                         I_bothC + I_bothE + duration + duration2 + duration3, 
                       data = estim, reflevel = "no_exit")
m1_TTH1 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                 I_bothC + I_bothE + duration + duration2 + duration3, 
               data = estim[list1, ], reflevel = "no_exit")
m1_TTH2 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                 I_bothC +  duration + duration2 + duration3, 
               data = estim[list2, ], reflevel = "no_exit")
m1_TTH3 = mlogit(next_year ~ 0 | sexe + generation_group2 + 
                 I_bothC +  duration + duration2 + duration3, 
               data = estim[list3, ], reflevel = "no_exit")
m1_TTH4 = glm(exit2 ~  sexe + generation_group2 + 
                    duration + duration2 + duration3, 
               data = data_est[list4, ], x=T, family=binomial("logit"))


save(m1_TTH1, m1_TTH2, m1_TTH3, m1_TTH4, file = paste0(save_model_path, "m1_by_grade.rda"))


m1 = extract.mlogit2(mlog1)
m2 = extract.mlogit2(mlog2)
m3 = extract.mlogit2(mlog3)
m4 = extract.mlogit2(mlog4)
m5 = extract.glm2(mlog5, include.aic =  F, include.bic = F, include.deviance =  F)

model.list <- list(m2, m3, m4, m5)

name.map <- list("exit_next:(intercept)"       = "exit_next: constante",
                 "exit_next:sexeM"             = "exit_next: Homme",  
                 "exit_next:generation_group22" = "exit_next: Generation 70s", 
                 "exit_next:generation_group23 "= "exit_next: Generation 80s", 
                 "exit_next:I_bothC"            = "exit_next: Conditions choix remplies",
                 "exit_next:I_bothE"            = "exit_next: Conditions exam remplies",
                 "exit_oth:(intercept)"        = "exit_oth: constante",              
                 "exit_oth:sexeM"              = "exit_oth: Homme",
                 "exit_oth:generation_group22" = "exit_oth: Generation 70s",
                 "exit_oth:generation_group23" = "exit_oth: Generation 80s",
                 "exit_oth:I_bothC"            = "exit_oth: Conditions choix remplies",
                 "exit_oth:I_bothE"            = "exit_oth: Conditions exam remplies",
                 "(intercept)"        = "Constante",              
                 "sexeM"              = "Homme",
                 "generation_group22" = "Generation 70s",
                 "generation_group23" = "Generation 80s")


oldnames <- all.varnames.dammit(model.list) 
ror <- build.ror(oldnames, name.map)

print(texreg2(model.list,
              caption.above=T,
              custom.model.names = c("TTH1", "TTH2","TTH3", "TTH4"),
              float.pos = "!ht",
              digit=3,
              stars = c(0.01, 0.05, 0.1),
              custom.coef.names=ror$ccn,   reorder.coef=ror$rc,  omit.coef=ror$oc,
              booktabs=T))




#### III. Sequential logit ####


### M1 : sortie ou non / destination

# Step 1: 
data_est$exit = ifelse(data_est$next_year == 'exit_oth' | data_est$next_year =='exit_next', 1, 0)

step1_m1 <- glm(exit ~  sexe + generation_group2 + grade + 
               I_bothC + I_bothE + duration + duration2 + duration3, 
              data=data_est, x=T, family=binomial("logit"))
# Step 2: 
data_est2 = data_est[which(data_est$exit == 1), ]
data_est2$exit_next = ifelse(data_est2$next_year =='exit_next', 1, 0)
step2_m1 <- glm(exit_next ~  sexe + generation_group2 + grade + 
               I_bothC + I_bothE + duration + duration2 + duration3, 
             data=data_est2 , x=T, family=binomial("logit"))


save(step1_m1, step2_m1, file = paste0(save_model_path, "m1_seq.rda"))


m1 = extract.glm2(step1_m1)
m2 = extract.glm2(step2_m1)
model.list <- list(m1, m2)


name.map <- list("(intercept)"        = "Constante",              
                 "sexeM"              = "Homme",
                 "generation_group22" = "Generation 70s",
                 "generation_group23" = "Generation 80s",
                 "gradeTTH2"     = "TTH2",
                 "gradeTTH3"     = "TTH3",
                 "gradeTTH4"     = "TTH4",
                 "I_bothC"            = "Conditions choix remplies",
                 "I_bothE"            = "Conditions exam remplies")


oldnames <- all.varnames.dammit(model.list) 
ror <- build.ror(oldnames, name.map)

print(texreg2(model.list,
              caption.above=T,
              custom.model.names = c("Etape 1: exit vs. no exit", "Etape 2: exit\\_next vs. exit\\_oth"),
              float.pos = "!ht",
              digit=3,
              stars = c(0.01, 0.05, 0.1),
              custom.coef.names=ror$ccn,   reorder.coef=ror$rc,  omit.coef=ror$oc,
              booktabs=T))



### M2 : sortie du corps? / changement de grade?

# Step 1: 
data_est$exit_corps = ifelse(data_est$next_year == 'exit_oth', 1, 0)

step1_m2 <- glm(exit_corps ~  sexe + generation_group2 + grade + duration + duration2 + duration3, 
             data=data_est, x=T, family=binomial("logit"))
# Step 2: 
data_est2 = data_est[which(data_est$exit_corps == 0), ]
data_est2$exit_next = ifelse(data_est2$next_year =='exit_next', 1, 0)
step2_m2 <- glm(exit_next ~  sexe + generation_group2 + grade + 
               I_bothC + I_bothE + duration + duration2 + duration3, 
             data=data_est2 , x=T, family=binomial("logit"))


save(step1_m2, step2_m2, file = paste0(save_model_path, "m2_seq.rda"))


m1 = extract.glm2(step1_m2)
m2 = extract.glm2(step2_m2)
model.list <- list(m1, m2)


name.map <- list("(intercept)"        = "Constante",              
                 "sexeM"              = "Homme",
                 "generation_group22" = "Generation 70s",
                 "generation_group23" = "Generation 80s",
                 "gradeTTH2"     = "TTH2",
                 "gradeTTH3"     = "TTH3",
                 "gradeTTH4"     = "TTH4",
                 "I_bothC"            = "Conditions choix remplies",
                 "I_bothE"            = "Conditions exam remplies")


oldnames <- all.varnames.dammit(model.list) 
ror <- build.ror(oldnames, name.map)

print(texreg2(model.list,
              caption.above=T,
              custom.model.names = c("Etape 1: Sortie corps? ", "Etape 2: Changement de grade?"),
              float.pos = "!ht",
              digit=3,
              stars = c(0.01, 0.05, 0.1),
              custom.coef.names=ror$ccn,   reorder.coef=ror$rc,  omit.coef=ror$oc,
              booktabs=T))



##### TEST NESTED ####
estim = mlogit.data(data_est, shape = "wide", choice = "next_year")



mlog0 = mlogit(next_year ~ 0 | 1, data = estim, reflevel = "no_exit")
mlog1 = mlogit(next_year ~ 0 | sexe + generation_group2, data = estim, reflevel = "no_exit")
mlog2 = mlogit(next_year ~ 0 | sexe + generation_group2 + grade, data = estim, reflevel = "no_exit")
mlog3 = mlogit(next_year ~ 0 | sexe + generation_group2 + grade + duration + duration2 + duration3, data = estim, reflevel = "no_exit")
mlog4 = mlogit(next_year ~ 0 | sexe + generation_group2 + grade + I_bothC, data = estim, reflevel = "no_exit")
mlog5 = mlogit(next_year ~ 0 | sexe + generation_group2 + grade + I_bothC + I_bothE, 
               data = estim, reflevel = "no_exit")

