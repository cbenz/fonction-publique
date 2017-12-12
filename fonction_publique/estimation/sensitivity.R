



################ Sensivitity analysis ################


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



#### II. Simulation ####
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

#### III. Results ####

## III.1 Exit rates ####

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




## III.2 Exit rates ####

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




