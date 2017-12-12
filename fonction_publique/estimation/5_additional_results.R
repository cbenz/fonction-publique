########### RESULTATS COMPLEMENTAIRES #######
# I. ANALYSE CONTREFACTUELLE 
# II. SENSIBILITE DES ESTIMATIONS
# III. OPTION DE MODELISATION EN REGROUPANT LES GRADES

################################################################
################ I. CF simulation ######################
################################################################

# Simulation of trajectories based two extrem cases: 
# 1. No change from 2011 to 2014. 
# 2. Everybody changes in 2011. 
# NB: only for TTH1-TTH3 et exit_next

#### I.1 Simulation ####

source(paste0(wd, "0_Outils_CNRACL.R")) 


output_global = generate_data_output(data_path)


for (m in 1:2)
{
  if (m == 1){modelname  =  "no_change"}  
  if (m == 2){modelname = "all_change"}
  print(paste0("Simulation for model ", modelname))
  for (annee in 2011:2014)
  { 
    print(paste0("Annee ", annee))
    if (annee == 2011)
    {
      data_sim = generate_data_sim(data_path, use = "min")
      output = data_sim[, c("ident", "annee", "grade","ib", "anciennete_dans_echelon", "echelon", "I_bothC")]
      output = rename(output, c("grade"=paste0("grade_", modelname) , 
                                "ib"=paste0("ib_", modelname), 
                                "anciennete_dans_echelon"=paste0("anciennete_dans_echelon_", modelname),
                                "echelon"=paste0("echelon_", modelname),
                                "I_bothC"=paste0("I_bothC_", modelname)))
      output[, paste0("situation_", modelname)] = NA
    }
    # Prediction of next_situation from estimated model 
    pred = data_sim
    pred$yhat =  "no_exit"
    if (m == 2 & annee == 2011){pred$yhat[which(pred$c_cir_2011 != "TTH4")] =  "exit_next"}
    # Save prediction for Py simulation
    output[which(output$annee == annee), paste0("situation_", modelname)] =  pred$yhat
    save_prediction_R(data = pred, annee, simul_path, modelname)
    # Prediction of next_ib using simulation.py
    launch_prediction_Py(annee, modelname)
    # Load 
    simul_py = load_simul_py(annee, modelname)
    # Incrementing data_sim for next year
    data_sim = increment_data_sim(data_sim, simul_py)
    
    # Save results
    output = save_results_simul(output, data_sim, modelname)
  }
  output_global = merge(output_global, output, by = c("ident", "annee"), all.x = T)
}

save(output_global, file = paste0(simul_path, "predictions_cf.Rdata"))

#### I.2 Results ####
load(file = paste0(simul_path, "predictions_cf.Rdata"))
output_global = output_global[-which(output_global$c_cir_2011 == "TTH4")]

# Obs
exit_obs      = extract_exit(output_global, "situation")
limits = c(0.5, 0.5, 0.3, 0.5)
p_obs = plot_share(exit_obs, plot = F, title = "Obs")
# Sim
list_models = c("all_change", "no_change")
for (m in (1:length(list_models)))
{
  var = paste0("situation_", list_models[m])  
  exit     = extract_exit(output_global, exit_var = var)
  p = plot_share(exit, plot = F, title =  list_models[m])
  assign(paste0("exit_",  list_models[m]), exit)  
  assign(paste0("p_",  list_models[m]), p)
}


table_masse_ib = function(data, var_ib, var_obs)
{
  data$var_ib = data[, var_ib]
  data$var_obs = data[, var_obs]
  
  print(paste0("Il y a ",(length(which(is.na(data$var_ib))))," obs avec ib = NA, que l'on supprime"  ))
  data = data[which(!is.na(data$var_ib)),]
  
  table = numeric(1)
  
  table[1] = sum(data$var_ib)/1e6
  table[2] = 100*(sum(data$var_ib)-sum(data$var_obs))/sum(data$var_obs)
  table[3] = sum(data$var_ib[which(data$annee == 2012)])/1e6
  table[4] = 100*(sum(data$var_ib[which(data$annee == 2012)]) - sum(data$var_obs[which(data$annee == 2012)]))/sum(data$var_obs[which(data$annee == 2012)])
  table[5] = sum(data$var_ib[which(data$annee == 2015)])/1e6
  table[6] = 100*(sum(data$var_ib[which(data$annee == 2015)]) - sum(data$var_obs[which(data$annee == 2015)]))/sum(data$var_obs[which(data$annee == 2015)])
  
  # list_grade = c("TTH1", "TTH2", "TTH3")
  # for (g in 1:length(list_grade))
  # {
  #   list = which(data$c_cir_2011 == list_grade[g])
  #   table[6 + 4*(g-1)+1] = sum(data$var_ib[list])/1e6
  #   table[6 + 4*(g-1)+2] = 100*(sum(data$var_ib[list]) - sum(data$var_obs[list])) /sum(data$var_obs[list])
  #   list = which(data$c_cir_2011 == list_grade[g] & data$annee == 2015)
  #   table[6 + 4*(g-1)+3] = sum(data$var_ib[list])/1e6
  #   table[6 + 4*(g-1)+4] = 100*(sum(data$var_ib[list]) - sum(data$var_obs[list])) /sum(data$var_obs[list])
  # }
  
  return(table)
}



obs = table_masse_ib(output_global, "ib", var_obs = "ib")
for (m in c("all_change", "no_change"))
{
  table = table_masse_ib(data = output_global, var_ib = paste0("ib_", m), var_obs = "ib")
  assign(paste0("table_masse_", m), table)  
}
table = cbind(obs, table_masse_all_change, table_masse_no_change)
colnames(table) = c('Observed', "Tous changent en 2011", "Aucun changement")
rownames(table) = c("Masse totale 2011-2015 (en 1e6)", "\\% diff par rapport a obs", 
                    "Masse totale 2012 (en 1e6)",  "\\% diff 2012 par rapport a obs",
                    "Masse totale 2015 (en 1e6)",  "\\% diff 2015 par rapport a obs"
                    # "Masse totale 2011-2015 TTH1 (en 1e6)", "\\% diff TTH1 par rapport a obs",
                    # "Masse totale 2015 TTH1 (en 1e6)", "\\% diff TTH1 2015 par rapport a obs",
                    # "Masse totale 2011-2015 TTH2 (en 1e6)", "\\% diff TTH2 par rapport a obs",
                    # "Masse totale 2015 TTH2 (en 1e6)", "\\% diff TTH2 2015 par rapport a obs",
                    # "Masse totale 2011-2015 TTH3 (en 1e6)", "\\% diff TTH3 par rapport a obs",
                    # "Masse totale 2015 TTH3 (en 1e6)", "\\% diff TTH3 2015 par rapport a obs",
                    
)


print(xtable(table,nrow = nrow(table), align = "l|ccc",
             ncol=ncol(table_movers)+1, byrow=T, digits = 2,
             caption = "Masses ib"),
      sanitize.text.function=identity,size="\\footnotesize", hline.after = c(0, 6),
      only.contents=T, include.colnames = T,
      file = paste0(fig_path,"masses_ib_cf.tex"))


table_gain_ib = function(data, var_ib, var_situation, details = F)
{
  data$var_ib = data[, var_ib]
  data$var_situation = data[, var_situation]
  data$next_ib = ave(data$var_ib, data$ident, FUN = shift1)
  data$gain_ib = data$next_ib - data$var_ib
  data$I_gain = ifelse(data$gain_ib >0, 1, 0)
  data$gain_ib_pct = 100*(data$gain_ib)/data$var_ib
  data = data[which(data$annee < 2015),]
  
  table = numeric(12)
  
  table[1] = mean(data$gain_ib, na.rm = T)
  table[2] = median(data$gain_ib_pct, na.rm = T)
  table[3] = 100*mean(data$I_gain, na.rm = T)
  
  list_grade = c("TTH1", "TTH2", "TTH3")
  for (g in 1:length(list_grade))
  {
    list = which(data$c_cir_2011 == list_grade[g])
    table[3*g+1] = mean(data$gain_ib[list], na.rm = T)
    table[3*g+2] = median(data$gain_ib_pct[list], na.rm = T)
    table[3*g+3] = 100*mean(data$I_gain[list], na.rm = T)
  }
  return(table)
}


obs = table_gain_ib(output_global, "ib", "situation", details = D)
for (m in c("all_change", "no_change"))
{
  table = table_gain_ib(data = output_global, var_ib = paste0("ib_", m), var_situation =  paste0("situation_", m), details = D)
  assign(paste0("table_gain_", m), table)  
}

table = cbind(obs, table_gain_all_change, table_gain_no_change)
colnames(table) = c('Observed', "Changement pour tous en 2011", "Aucun changement en 2011-2014" )
rownames(table) = c("gain ib moyen", "gain ib median en \\%", "\\% gain ib > 0",
                    "gain ib moyen TTH1", "gain ib median en \\% TTH1", "\\% gain ib > 0  TTH1",
                    "gain ib moyen TTH2", "gain ib median en \\% TTH2", "\\% gain ib > 0  TTH2",
                    "gain ib moyen TTH3", "gain ib median en \\% TTH3", "\\% gain ib > 0 TTH3")

print(xtable(table,nrow = nrow(table), align = "l|ccc", caption = "Gains ib",
             ncol=ncol(table_movers)+1, byrow=T, digits = 2),
      sanitize.text.function=identity,size="\\footnotesize",
      only.contents=F, include.colnames = T,
      file = paste0(fig_path,"gain_ib_cf.tex"))




################################################################
################ II. Sensivitity analysis ######################
################################################################

## Comparaison of the results with two alternatives: 
# 1. Different definition of the duration spent in grade 
# 2. Estimation on years 2011-2014 and not 2011 only. 


# Main data
source(paste0(wd, "0_Outils_CNRACL.R"))
datasets = load_and_clean(data_path, dataname = "filter/data_ATT_2011_filtered_after_duration_var_added_new.csv")
data_max = datasets[[1]]
data_min = datasets[[2]]

# Sample selection
data_est_max = data_max
data_est_max$first_grade =  ifelse(data_est_max$c_cir_2011 == "TTH1", 1, 0)
data_est_max$next_year = as.character(data_est_max$next_grade_situation)
data_est_max1 = data_est_max[which(data_est_max$left_censored == F & data_est_max$annee == 2011 & data_est_max$generation < 1990),]
data_est_max1 = create_variables(data_est_max1)  
data_est_max2 = data_est_max[which(data_est_max$left_censored == F & data_est_max$annee >= 2011  & data_est_max$annee <= 2014 & data_est_max$generation < 1990),]
data_est_max2 = create_variables(data_est_max2)  

data_est_min = data_min
data_est_min$first_grade  =  ifelse(data_est_min$c_cir_2011 == "TTH1", 1, 0)

data_est_min$next_year = as.character(data_est_min$next_grade_situation)
data_est_min1 = data_est_min[which(data_est_min$left_censored == F & data_est_min$annee == 2011 & data_est_min$generation < 1990),]
data_est_min1 = create_variables(data_est_min1)  
data_est_min2 = data_est_min[which(data_est_min$left_censored == F & data_est_min$annee >= 2011 & data_est_min$annee <= 2014 & data_est_min$generation < 1990),]
data_est_min2 = create_variables(data_est_min2)  



#### I. Descriptive statistics: comparison of duration  ####



data_est_min1$duree_min = data_est_min1$time
data_est_min1$duree_max = data_est_max1$time
data_est_min1$diff_duree = data_est_min1$duree_max - data_est_min1$duree_min
table(diff_duree)
aggregate( diff_duree ~ c_cir_2011, data_est_min1, table )


list_same_duration = which(data_est_min1$diff_duree == 0)
data_est_min1 = data_est_min1[list_same_duration,]
data_est_max1 = data_est_max1[list_same_duration,]

#### I. Estimation ####

estim1 = mlogit.data(data_est_max1, shape = "wide", choice = "next_year")
estim2 = mlogit.data(data_est_max2, shape = "wide", choice = "next_year")
estim3 = mlogit.data(data_est_min1, shape = "wide", choice = "next_year")
estim4 = mlogit.data(data_est_min2, shape = "wide", choice = "next_year")


mlog1 = mlogit(next_year ~ 0 | sexe + generation_group2 + grade + 
                 I_bothC + I_bothE:first_grade + duration + duration2, 
               data = estim1, reflevel = "no_exit")
mlog2 = mlogit(next_year ~ 0 | sexe + generation_group2 + grade + 
                 I_bothC + I_bothE:first_grade + duration + duration2, 
               data = estim2, reflevel = "no_exit")
mlog3 = mlogit(next_year ~ 0 | sexe + generation_group2 + grade + 
                 I_bothC + I_bothE:first_grade + duration + duration2, 
               data = estim3, reflevel = "no_exit")
mlog4 = mlogit(next_year ~ 0 | sexe + generation_group2 + grade + 
                 I_bothC + I_bothE:first_grade + duration + duration2, 
               data = estim4, reflevel = "no_exit")



list_comp = list(mlog1, mlog2, mlog3, mlog4)


# bundle up some models
m1 = extract.mlogit2(mlog1, include.aic =  T )
m2 = extract.mlogit2(mlog2, include.aic =  T )
m3 = extract.mlogit2(mlog3, include.aic =  T )
m4 = extract.mlogit2(mlog4, include.aic =  T )

model.list <- list(m1, m2, m3, m4)

name.map <- list("exit_next:(intercept)"       = "exit_next: constante",
                 "exit_next:sexeM"             = "exit_next: Homme",  
                 "exit_next:generation_group22"= "exit_next: Generation 70s", 
                 "exit_next:generation_group23"= "exit_next: Generation 80s", 
                 "exit_next:duration"          = "exit_next: Duree dans le grade", 
                 "exit_next:duration2"         = "exit_next: Duree dans le grade2 ", 
                 "exit_next:gradeTTH2"    = "exit_next: TTH2",  
                 "exit_next:gradeTTH3"    = "exit_next: TTH3", 
                 "exit_next:gradeTTH4"    = "exit_next: TTH4",
                 "exit_next:I_bothC"            = "exit_next: Conditions choix remplies",
                 "exit_next:I_bothE:first_grade"            = "exit_next: Conditions exam remplies",
                 "exit_next:I_echC"            = "exit_next: Conditions echelon choix remplies",
                 "exit_next:I_echE:first_grade"            = "exit_next: Conditions echelon exam remplies  x TTH1",
                 "exit_oth:(intercept)"        = "exit_oth: constante",              
                 "exit_oth:sexeM"              = "exit_oth: Homme",
                 "exit_oth:generation_group22" = "exit_oth: Generation 70s",
                 "exit_oth:generation_group23" = "exit_oth: Generation 80s",
                 "exit_oth:duration"          = "exit_oth: Duree dans le grade", 
                 "exit_oth:duration2"         = "exit_oth: Duree dans le grade2 ", 
                 "exit_oth:gradeTTH2"     = "exit_oth: TTH2",
                 "exit_oth:gradeTTH3"     = "exit_oth: TTH3",
                 "exit_oth:gradeTTH4"     = "exit_oth: TTH4",
                 "exit_oth:I_bothC"            = "exit_oth: Conditions choix remplies",
                 "exit_oth:I_bothE:first_grade"            = "exit_oth: Conditions exam remplies x TTH1",
                 "exit_oth:I_echC"            = "exit_oth: Conditions echelon choix remplies",
                 "exit_oth:I_echE:first_grade"            = "exit_oth: Conditions echelon exam remplies")


oldnames <- all.varnames.dammit(model.list) 
ror <- build.ror(oldnames, name.map)


print(texreg2(model.list,
              caption.above=F,
              float.pos = "!ht",
              digit=3,
              stars = c(0.01, 0.05, 0.1),
              hline.after = c(0, length(name.map)/2, length(name.map)),
              custom.coef.names=ror$ccn,   reorder.coef=ror$rc, # omit.coef=ror$oc,
              booktabs=T) )



#### II.2 Simulation ####
output_global = generate_data_output(data_path)

for (m in 1:4)
{
  modelname  =  paste0("mlog", toString(m))
  
  print(paste0("Simulation for model ", modelname))
  for (annee in 2011:2014)
  { 
    print(paste0("Annee ", annee))
    if (annee == 2011)
    {
      if (m<=2){data_sim = generate_data_sim(data_path, use = "max")}
      if (m>=3){data_sim = generate_data_sim(data_path, use = "min")}
      output = data_sim[, c("ident", "annee", "grade","ib", "anciennete_dans_echelon", "echelon", "I_bothC")]
      output = rename(output, c("grade"=paste0("grade_", modelname) , 
                                "ib"=paste0("ib_", modelname), 
                                "anciennete_dans_echelon"=paste0("anciennete_dans_echelon_", modelname),
                                "echelon"=paste0("echelon_", modelname),
                                "I_bothC"=paste0("I_bothC_", modelname)))
      output[, paste0("situation_", modelname)] = NA
    }
    # Prediction of next_situation from estimated model 
    pred =  predict_next_year_MNL(data_sim, model = list_comp[[m]], modelname)
    stopifnot(length(which(pred$yhat == "exit_next" & pred$grade == "TTH4")) == 0)
    # Save prediction for Py simulation
    output[which(output$annee == annee), paste0("situation_", modelname)] = pred$yhat
    save_prediction_R(data = pred, annee, simul_path, modelname)
    # Prediction of next_ib using simulation.py
    launch_prediction_Py(annee, modelname)
    # Load 
    simul_py = load_simul_py(annee, modelname)
    # Incrementing data_sim for next year
    data_sim = increment_data_sim(data_sim, simul_py)
    
    # Save results
    output = save_results_simul(output, data_sim, modelname)
  }
  output_global = merge(output_global, output, by = c("ident", "annee"), all.x = T)
}

#### II.3 Results ####



# Obs
exit_obs      = extract_exit(output_global, "situation")
exit_obs_TTH1 = extract_exit(output_global[which(output_global$c_cir_2011 == "TTH1"), ], "situation")
exit_obs_TTH2 = extract_exit(output_global[which(output_global$c_cir_2011 == "TTH2"), ], "situation")
exit_obs_TTH3 = extract_exit(output_global[which(output_global$c_cir_2011 == "TTH3"), ], "situation")
exit_obs_TTH4 = extract_exit(output_global[which(output_global$c_cir_2011 == "TTH4"), ], "situation")
p_obs = plot_share(exit_obs, plot = F, title = "Obs")
p_obs_TTH1 =  plot_share(exit_obs_TTH1, plot = F, title = "Obs")
p_obs_TTH2 =  plot_share(exit_obs_TTH2, plot = F, title = "Obs")
p_obs_TTH3 =  plot_share(exit_obs_TTH3, plot = F, title = "Obs")
p_obs_TTH4 =  plot_share(exit_obs_TTH4, plot = F, title = "Obs")
# Sim
count = 0
for (m in c("mlog1", "mlog2", "mlog3","mlog4" ))
{
  count = count + 1
  var = paste0("situation_", m)  
  exit     = extract_exit(output_global, exit_var = var)
  p = plot_share(exit_obs, plot = F, title = m)
  assign(paste0("exit_", m), exit)  
  assign(paste0("p_", m), p)
  for (g in c("TTH1", "TTH2", "TTH3", "TTH4"))
  {
    exit = extract_exit(output_global[which(output_global$c_cir_2011 == g), ], var)
    p = plot_share(exit, plot = F, title = paste0("Model ", count))
    assign(paste0("exit_", m,"_",g), exit)  
    assign(paste0("p_", m,"_",g), p)  
  }
}


pdf(paste0(fig_path,"exit_comp_TTH2_sens.pdf"), onefile=FALSE)
grid_arrange_shared_legend(p_obs_TTH2, p_mlog1_TTH2, p_mlog2_TTH2, p_mlog3_TTH2, p_mlog4_TTH2, 
                           ncol = 5, nrow = 1)
dev.off()

pdf(paste0(fig_path,"exit_comp_TTH3_sens.pdf"), onefile=FALSE)
grid_arrange_shared_legend(p_obs_TTH3, p_mlog1_TTH3, p_mlog2_TTH3, p_mlog3_TTH3, p_mlog4_TTH3, 
                           ncol = 5, nrow = 1)
dev.off()


# Ecart predit/observé pour grade et ib
list_pbl =  ""
for (m in c("mlog1","mlog2", "mlog3", "mlog4"))
{
  var = paste0("ib_", m)
  list_pbl_id = unique(output_global$ident[which(is.na(output_global[, var]))])
  list_pbl = c(list_pbl, list_pbl_id)
  list_pbl = unique(list_pbl)
}
output_global_cleared = output_global[which(!is.element(output_global$ident, list_pbl)),]


table_ind = function(data, var_ib, var_situation)
{
  data = data[which(data$annee > 2011), ]
  data$ib_obs = data[, "ib"]
  data$situation_obs = data[, "situation"]
  data$ib_sim = data[, var_ib]
  data$situation_sim = data[, var_situation]
  data$diff_ib = (data$ib_sim - data$ib_obs)
  data$diff_ib_abs = abs(data$ib_sim - data$ib_obs)
  
  table = numeric(12)
  
  # Proportion same situation
  table[1] = length(which(data$situation_obs == data$situation_sim))/length(data$situation_obs)
  list = which(data$situation_obs == "no_exit")
  table[2] = length(which(data$situation_obs[list] == data$situation_sim[list]))/length(list)
  list = which(data$situation_obs == "exit_next")
  table[3] = length(which(data$situation_obs[list] == data$situation_sim[list]))/length(list)
  list = which(data$situation_obs == "exit_oth")
  table[4] = length(which(data$situation_obs[list] == data$situation_sim[list]))/length(list)
  # Ecart ib  
  table[5] = mean(data$diff_ib, na.rm = T)
  table[6:8] = as.numeric(quantile(data$diff_ib, na.rm = T)[3:5])
  table[9] = mean(data$diff_ib_abs, na.rm = T)
  table[10:12] = as.numeric(quantile(data$diff_ib_abs, na.rm = T)[3:5])
  table[13] = mean(data$diff_ib[which(data$annee == 2012)], na.rm = T)
  table[14] = mean(data$diff_ib[which(data$annee == 2015)], na.rm = T)
  # Ecart moyen au carré
  table[15] = rmse(data$ib_sim, data$ib_obs)
  return(table)
}


for (m in c("mlog1","mlog2", "mlog3", "mlog4"))
{
  table = table_ind(data = output_global_cleared, var_ib = paste0("ib_", m) , var_situation = paste0("situation_", m) )
  assign(paste0("table_ind_", m), table)  
}

table_all = cbind(table_ind_mlog1, table_ind_mlog2, table_ind_mlog3, table_ind_mlog4)
colnames(table_all) = c("Modele 1","Modele 2", "Modele 3", "Modele 4")
rownames(table_all) = c("\\% bonne prediction etat", "\\% bonne prediction quand obs = no exit",
                        "\\% bonne prediction etat quand obs = exit next",
                        "\\% bonne prediction etat quand obs = exit oth",
                        "Ecart IB moyen", "Q2 ecart IB ","Q3 ecart IB ","Q4 ecart IB ",
                        "Ecart IB moyen (abs)", "Q2 ecart IB (abs)","Q3 ecart IB (abs)","Q4 ecart IB (abs)",
                        "Ecart IB moyen en 2011","Ecart IB moyen en 2014", "RMSE")

print(xtable(table_all,nrow = nrow(table_all), align = "l|cccc", caption =  "Ecart observe simule",
             ncol=ncol(table_all)+1, byrow=T, digits = 2),
      sanitize.text.function=identity,size="\\footnotesize", hline.after = c(0, 4, 7, 10, 12),
      only.contents=F, include.colnames = T)
file = paste0(fig_path,"ecarts_sens.tex"))






###############################################################################################
######### III. Fusion #########
################################################################################################
 
## III.1 Estimation ####
source(paste0(wd, "0_Outils_CNRACL.R"))
datasets = load_and_clean(data_path, dataname = "filter/data_ATT_2011_filtered_after_duration_var_added_new.csv")
data_max = datasets[[1]]
data_min = datasets[[2]]

# Sample selection
data_est = data_min
data_est = data_est[which(data_est$left_censored == F & data_est$annee == 2011 & data_est$generation < 1990),]
data_est = create_variables(data_est)  

data_est$grade2 = data_est$grade
data_est$grade2[which(data_est$grade2 == "TTH3")] = "TTH2"
# Data for MNL estimation
data_est$next_year = as.character(data_est$next_grade_situation)
estim = mlogit.data(data_est, shape = "wide", choice = "next_year")


mlog1 = mlogit(next_year ~ 0 | sexe + generation_group2 + grade + duration + duration2 + I_condC + I_condE, 
               data = estim, reflevel = "no_exit")
mlog2 = mlogit(next_year ~ 0 | sexe + generation_group2 + grade2 + duration + duration2 + I_condC + I_condE, 
               data = estim, reflevel = "no_exit")

list_MNL_fusion = list(mlog1, mlog2)
save(list_MNL, file = paste0(save_model_path, "mlog.rda"))

# bundle up some models
m1 = extract.mlogit2(mlog1, include.aic =  T )
m2 = extract.mlogit2(mlog2, include.aic =  T )


model.list <- list(m1, m2)

name.map <- list("exit_next:(intercept)"       = "exit_next: constante",
                 "exit_next:gradeTTH2"    = "exit_next: TTH2",  
                 "exit_next:gradeTTH3"    = "exit_next: TTH3", 
                 "exit_next:gradeTTH4"    = "exit_next: TTH4",
                 "exit_next:grade2TTH2"     = "exit_next: Grade intermédiaire",
                 "exit_next:grade2TTH4"     = "exit_next: Grade final",
                 "exit_next:I_condC"            = "exit_next: Conditions choix remplies",
                 "exit_next:I_condE"            = "exit_next: Conditions exam remplies",
                 "exit_oth:(intercept)"       = "exit_oth: constante",
                 "exit_oth:gradeTTH2"     = "exit_oth: TTH2",
                 "exit_oth:gradeTTH3"     = "exit_oth: TTH3",
                 "exit_oth:gradeTTH4"     = "exit_oth: TTH4",
                 "exit_oth:grade2TTH2"     = "exit_oth: Grade intermédiaire",
                 "exit_oth:grade2TTH4"     = "exit_oth: Grade final",
                 "exit_oth:I_condC"       = "exit_oth: Conditions choix remplies",
                 "exit_oth:I_condE"       = "exit_oth: Conditions exam remplies")


oldnames <- all.varnames.dammit(model.list) 
ror <- build.ror(oldnames, name.map)

print(texreg2(model.list,
              caption.above=F,
              float.pos = "!ht",
              digit=3,
              stars = c(0.01, 0.05, 0.1),
              custom.coef.names=ror$ccn,   reorder.coef=ror$rc,  omit.coef=ror$oc,
              booktabs=T))

## III.2 Simulation ####


output_global = generate_data_output(data_path)

add = generate_data_output(data_path)

for (m in 1:2)
{
  modelname  =  paste0("MNL_", toString(m))  
  print(paste0("Simulation for model ", modelname))
  for (annee in 2011:2011)
  { 
    print(paste0("Annee ", annee))
    if (annee == 2011)
    {
      data_sim = generate_data_sim(data_path, use = "min")
      data_sim$grade2 = data_sim$grade
      data_sim$grade2[which(data_sim$grade2 == "TTH3")] = "TTH2"
      output = data_sim[, c("ident", "annee", "grade","ib", "anciennete_dans_echelon", "echelon", "I_bothC")]
      output = rename(output, c("grade"=paste0("grade_", modelname) , 
                                "ib"=paste0("ib_", modelname), 
                                "anciennete_dans_echelon"=paste0("anciennete_dans_echelon_", modelname),
                                "echelon"=paste0("echelon_", modelname),
                                "I_bothC"=paste0("I_bothC_", modelname)))
      output[, paste0("situation_", modelname)] = NA
    }
    # Prediction of next_situation from estimated model 
    pred =  predict_next_year_MNL(data_sim, model = list_MNL_fusion[[m]], modelname) 
  
    stopifnot(length(which(pred$yhat == "exit_next" & pred$grade == "TTH4")) == 0)
    # Save prediction for Py simulation
    output[which(output$annee == annee), paste0("situation_", modelname)] = pred$yhat
    
    # Check 
    list_id1 = output$ident[which(output$annee == annee & output$situation_BG_1 == "exit_next")]
    list_id2 = pred$ident[which(pred$yhat == "exit_next")]
    stopifnot(length(setdiff(list_id1, list_id2))==0)
    
    save_prediction_R(data = pred, annee, simul_path, modelname)
    # Prediction of next_ib using simulation.py
    launch_prediction_Py(annee, modelname)
    # Load 
    simul_py = load_simul_py(annee, modelname)
    # Incrementing data_sim for next year
    data_sim = increment_data_sim(data_sim, simul_py)
    
    # Save results
    output = save_results_simul(output, data_sim, modelname)
  }
  output_global = merge(output_global, output, by = c("ident", "annee"), all.x = T)
}

save(output_global, file = paste0(simul_path, "predictions_fusion.Rdata"))




# Proba de sortie vers grade next par grade et par échelon
subdata = output_global[which(output_global$annee == 2011 & output_global$c_cir_2011 != "TTH4"),]
subdata$situation_obs = subdata$situation
subdata$duration = 2011- subdata$annee_entry_min + 1

var = c("ident", "c_cir_2011", "echelon", "duration", "situation_obs", "situation_MNL_1","situation_MNL_2")
subdata = subdata[, var]
df <- melt(subdata, id.vars = c(1:4), value.name = "next_year",  variable.name = "model")
df$model = substring(df$model, 11)
df$exit = ifelse(df$next_year == "exit_next", 1, 0)


comp_exit_by_ech = function(df, save = F, list_models, n_col, legend = F, grade)
{
  df = df[which(df$c_cir_2011 == grade),]
  
  ech = seq(range(df$echelon)[1],range(df$echelon)[2])
  hazard = matrix(ncol = length(ech), nrow = length(list_models))
  effectif = numeric(length(ech))
  
  for (m in 1:length(list_models))
  {
    subdf = df[which(df$model == list_models[m]),] 
    for (e in 1:length(ech))
    {
      if (m ==1){effectif[e] = length(which(subdf$echelon == ech[e]))}
      hazard[m, e] =   length(which(subdf$echelon == ech[e] & subdf$exit == 1))/length(which(subdf$echelon == ech[e]))
    }
  }  
  par(mar = c(4,4,1,1))
  lim = c(0, max(hazard, na.rm = T))
  plot(ech, rep(NA, length(ech)), ylim = lim, xlab = "ECHELON", ylab = "% EXIT NEXT GRADE")
  for (m in 1:length(list_models))
  {
    lines(ech ,hazard[m, ], type = "l", lty = 1, lwd = 3, col = n_col[m])
  }
  par(new = T)
  plot(ech, effectif, type ="l", lty = 2, lwd = 1, axes=F, xlab=NA, ylab=NA)
  if (legend){legend("topleft", legend = c("Hazard", "Nb obs."), lwd = 3, lty = c(1,3), col = c("darkcyan", "black"), cex = 1.1)}
}  


comp_exit_by_dur = function(df, save = F, list_models = c("obs", "MNL_2", "MNL_3", "BG_1"), n_col, legend = F, grade)
{
  df = df[which(df$c_cir_2011 == grade),]
  
  dur = seq(range(df$duration)[1],range(df$duration)[2])
  hazard = matrix(ncol = length(dur), nrow = length(list_models))
  effectif = numeric(length(dur))
  
  for (m in 1:length(list_models))
  {
    subdf = df[which(df$model == list_models[m]),] 
    for (e in 1:length(dur))
    {
      if (m ==1){effectif[e] = length(which(subdf$duration == dur[e]))}
      hazard[m, e] =   length(which(subdf$duration == dur[e] & subdf$exit == 1))/length(which(subdf$duration == dur[e]))
    }
  }  
  par(mar = c(4,4,1,1))
  lim = c(0, max(hazard, na.rm = T))
  plot(dur, rep(NA, length(dur)), ylim = lim, xlab = "DUREE DANS LE GRADE", ylab = "% EXIT NEXT GRADE")
  for (m in 1:length(list_models))
  {
    lines(dur ,hazard[m, ], type = "l", lty = 1, lwd = 3, col = n_col[m])
  }
  par(new = T)
  plot(dur, effectif, type ="l", lty = 2, lwd = 1, axes=F, xlab=NA, ylab=NA)
  if (legend){legend("topleft", legend = c("Hazard", "Nb obs."), lwd = 3, lty = c(1,3), col = c("darkcyan", "black"), cex = 1.1)}
}  


list_models = c("obs", "MNL_1", "MNL_2")
list_names =  c("obs", "Avec 4 grades", "Avec 3 grades")

n_col <- c("black", "#727272","#f1595f","#79c36a","#599ad3", "#f9a65a", "#9e66ab", "#cd7058","#d77fb3")
for (grade in c("TTH1", "TTH2", "TTH3"))
{
  pdf(paste0(fig_path, "comp_exit_pred_",grade,"_fusion.pdf"))
  layout(matrix(c(1,2,3, 3), nrow=2,ncol=2, byrow=F), heights =  c(3,3), widths = c(4,2))
  # Graphe by ech
  comp_exit_by_ech(df, list_models = list_models, n_col = n_col, grade = grade)
  # Graphe by dur
  comp_exit_by_dur(df, list_models = list_models, n_col = n_col, grade = grade) 
  # Legend
  par(mar=c(0,0,0,0),font=1.5)
  plot.new()
  legend("left", legend=c(list_names, "Nb \nd'obs\n"), lty=c(rep(1, length(list_names)), 2), title = "Modèles",
         col=c(n_col[1:length(list_names)],"black"),lwd=3,cex=1.2, ncol=1, bty = "n")
  dev.off()
  
}




