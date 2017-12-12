################ CF simulation################


# Simulation of trajectories based two extrem cases: 
# 1. No change from 2011 to 2014. 
# 2. Everybody changes in 2011. 
# NB: only for TTH1-TTH3 et exit_next

#### I. Simulation ####

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

#### II. Results ####




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


grid_arrange_shared_legend(p_obs, p_all_change, p_no_change, ncol = 3, nrow = 1)


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






