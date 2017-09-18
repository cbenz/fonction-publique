

#################################  Simulation diagnosis ###############################
# Comparing predicted and observed outcomes 
# I. Grade : we compare observed and simulated exit from initial grade by grade and destination
# II. IB
 

### 0. Initialisation ####

source(paste0(wd, "0_Outils_CNRACL.R")) 
# Load results
load(paste0(simul_path, "predictions.Rdata"))

########## I. Exit grade 2011-2014   ##########


## I.1 Compute exit rates and drawing plot ####

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
for (m in c("MNL_2", "MNL_3", "BG_1","MS_1" ))
{
var = paste0("situation_", m)  
exit     = extract_exit(output_global, exit_var = var)
p = plot_share(exit_obs, plot = F, title = m)
assign(paste0("exit_", m), exit)  
assign(paste0("p_", m), p)
  for (g in c("TTH1", "TTH2", "TTH3", "TTH4"))
  {
    exit = extract_exit(output_global[which(output_global$c_cir_2011 == g), ], var)
    p = plot_share(exit, plot = F, title = m)
    assign(paste0("exit_", m,"_",g), exit)  
    assign(paste0("p_", m,"_",g), p)  
  }
}
  
pdf(paste0(fig_path,"exit_obs_all.pdf"))
p_obs
dev.off()

pdf(paste0(fig_path,"exit_obs_byG.pdf"), onefile=FALSE)
grid_arrange_shared_legend(p1, p2, p3, p4, ncol = 2, nrow = 2)
dev.off()

pdf(paste0(fig_path,"exit_comp_all.pdf"), onefile=FALSE)
grid_arrange_shared_legend(p_obs, p_MNL_2, p_MNL_3, p_BG_1, p_MS_1)
dev.off()

pdf(paste0(fig_path,"exit_comp_TTH1.pdf"), onefile=FALSE)
grid_arrange_shared_legend(p_obs_TTH1,p_MNL_2_TTH1, p_MNL_3_TTH1, p_BG_1_TTH1, p_MS_1_TTH1)
dev.off()

pdf(paste0(fig_path,"exit_comp_TTH2.pdf"), onefile=FALSE)
grid_arrange_shared_legend(p_obs_TTH2,p_MNL_2_TTH2, p_MNL_3_TTH2, p_BG_1_TTH2, p_MS_1_TTH2)
dev.off()

pdf(paste0(fig_path,"exit_comp_TTH3.pdf"), onefile=FALSE)
grid_arrange_shared_legend(p_obs_TTH3,p_MNL_2_TTH3, p_MNL_3_TTH3, p_BG_1_TTH3, p_MS_1_TTH3)
dev.off()

pdf(paste0(fig_path,"exit_comp_TTH4.pdf"), onefile=FALSE)
grid_arrange_shared_legend(p_obs_TTH4,p_MNL_2_TTH4, p_MNL_3_TTH4, p_BG_1_TTH4, p_MS_1_TTH4)
dev.off()


## I.2 Caracteristics of movers in 2011 ####

# Caracteristics of movers

movers_characteristics = function(data, exit_var)
{  
  table_movers = numeric(22)
  data$exit = data[, exit_var]
  data$age = 2011 - data$generation
  data$femme =ifelse(data$sexe == "F", 1, 0)
  data = data[which(data$annee == 2011),]
  # All
  table_movers[1] = 100*length(which(exit[] == "exit_next"))/length(exit[])
  table_movers[2] = 100*length(which(exit[] == "exit_oth"))/length(exit[])                              
  # Women
  list = which(data$exit == "exit_next")
  table_movers[3] = 100*mean(data$femme[list])
  list = which(data$exit == "exit_oth")
  table_movers[4] = 100*mean(data$femme[list])
  # Age
  list = which(data$exit == "exit_next")
  table_movers[5] = mean(data$age[list])
  list = which(data$exit == "exit_oth")
  table_movers[6] = mean(data$age[list])
  # TTH1
  list = which(data$c_cir_2011 == "TTH1")
  table_movers[7] = 100*length(which(data$exit[list] == "exit_next"))/length(data$exit[list])
  table_movers[8] = 100*length(which(data$exit[list] == "exit_oth"))/length(data$exit[list])  
  # TTH2
  list = which(data$c_cir_2011 == "TTH2")
  table_movers[9] = 100*length(which(data$exit[list] == "exit_next"))/length(data$exit[list])
  table_movers[10] = 100*length(which(data$exit[list] == "exit_oth"))/length(data$exit[list])  
  # TTH3
  list = which(data$c_cir_2011 == "TTH3")
  table_movers[11] = 100*length(which(data$exit[list] == "exit_next"))/length(data$exit[list])
  table_movers[12] = 100*length(which(data$exit[list] == "exit_oth"))/length(data$exit[list])  
  # TTH4
  list = which(data$c_cir_2011 == "TTH4")
  table_movers[13] = 100*length(which(data$exit[list] == "exit_next"))/length(data$exit[list])
  table_movers[14] = 100*length(which(data$exit[list] == "exit_oth"))/length(data$exit[list])  
  # IB distrib
  list = which(data$exit == "exit_next")
  table_movers[15] = mean(data$ib[list])
  table_movers[16:18] = as.numeric(quantile(data$ib[list])[2:4])
  list = which(data$exit == "exit_oth")
  table_movers[19] = mean(data$ib[list])
  table_movers[20:22] = as.numeric(quantile(data$ib[list])[2:4])
  return(table_movers)
}  

table_obs =  movers_characteristics(output_global, exit_var = "situation")
for (m in c("MNL_2", "MNL_3", "BG_1","MS_1"))
{
  var = paste0("situation_", m)  
  table     = movers_characteristics(output_global, exit_var = var)
  assign(paste0("table_", m), table)  
}

table_movers = cbind(table_obs, table_MNL_2, table_MNL_3, table_BG_1, table_MS_1)
colnames(table_movers) = c('Observed', "MNL\\_2", "MNL\\_3", "BG\\_1", "MS\\_1")
rownames(table_movers) = c("\\% exit next All", "\\% exit oth All", 
                           "\\% Women when exit next", "\\% Women when exit oth",
                           "Mean age when exit next", "Mean age  when exit oth",
                           "\\% exit next TTH1", "\\% exit oth TTH1", "\\% exit next TTH2", "\\% exit oth TTH2",
                           "\\% exit next TTH3", "\\% exit oth TTH3", "\\% exit next TTH4", "\\% exit oth TTH4",
                           "Mean IB when exit next", "Q1 IB when exit next", "Q2 IB when exit next","Q3 IB when exit next",
                           "Mean IB when exit oth", "Q1 IB when exit oth", "Q2 IB when exit oth","Q3 IB when exit oth")

mdigit <- matrix(c(rep(2,(ncol(table_movers)+1)*14),rep(0,(ncol(table_movers)+1)*8)),
                 nrow = nrow(table_movers), ncol=ncol(table_movers)+1, byrow=T)                           
print(xtable(table_movers,nrow = nrow(table_movers), 
             ncol=ncol(table_movers)+1, byrow=T, digits = mdigit),
      sanitize.text.function=identity,size="\\footnotesize", hline.after = c(0, 2, 4, 6, 8, 10, 12, 14, 18),
      only.contents=F, include.colnames = T)





############ II. IB #############


## II. 1 Plot distributions ####

plot_distrib_ib_by_year = function(data, var)
{
# Drop ib above 500
data$var = data[, var]  
list_id = data$ident[which(data$var > 500)]
data = data[which(!is.element(data$ident, list_id)),]
# Plot density
ncolors = c("grey60", "grey30", "black")
myData <- data.frame("2011" = data$ib[which(data$annee == 2011)],
                     "2013" = data$ib[which(data$annee == 2013)],
                     "2015" = data$ib[which(data$annee == 2015)]
                     )
dens <- apply(myData, 2, density)
par(mar=c(4,4.1,1,0.2))
plot(NA, xlim=range(sapply(dens, "[", "x")), ylim=range(sapply(dens, "[", "y")), xlab = "IB", ylab = "DENSITE")
mapply(lines, dens, col=ncolors, lwd = 3)
legend("topright", legend= c(2011, 2013, 2015), fill=ncolors)
}

pdf(paste0(fig_path,"dist_ib_all.pdf"))
plot_distrib_ib_by_year(data = output_global, var = "ib") 
dev.off()

pdf(paste0(fig_path,"dist_ib_byG.pdf"))
par(mfrow=c(2,2))
plot_distrib_ib_by_year(data = output_global[which(output_global$c_cir_2011 == "TTH1"),], var = "ib") 
title("TTH1")
plot_distrib_ib_by_year(data = output_global[which(output_global$c_cir_2011 == "TTH2"),], var = "ib") 
title("TTH2")
plot_distrib_ib_by_year(data = output_global[which(output_global$c_cir_2011 == "TTH3"),], var = "ib") 
title("TTH3")
plot_distrib_ib_by_year(data = output_global[which(output_global$c_cir_2011 == "TTH4"),], var = "ib") 
title("TTH4")
dev.off()



## II. 2 Table ####


table_masse_ib = function(data, var_ib)
{
  data$var_ib = data[, var_ib]
  
  print(paste0("Il y a ",(length(which(is.na(data$var_ib))))," obs avec ib = NA, que l'on supprime"  ))
  data = data[which(!is.na(data$var_ib)),]
  
  table = numeric(1)
  
  table[1] = sum(data$var_ib)/1e6
  table[2] = sum(data$var_ib[which(data$annee == 2012)])/1e6
  table[3] = sum(data$var_ib[which(data$annee == 2015)])/1e6
  
  list_grade = c("TTH1", "TTH2", "TTH3", "TTH4")
  for (g in 1:length(list_grade))
  {
    table[3*g+1] = sum(data$var_ib[which(data$c_cir_2011 == list_grade[g])])/1e6
    table[3*g+2] = sum(data$var_ib[which(data$annee == 2012 & data$c_cir_2011 == list_grade[g])])/1e6
    table[3*g+3] = sum(data$var_ib[which(data$annee == 2015 & data$c_cir_2011 == list_grade[g])])/1e6    
  }

  return(table)
}



obs = table_masse_ib(output_global, "ib")
for (m in c("MNL_1","MNL_2", "MNL_3", "BG_1","MS_1" ))
{
  table = table_masse_ib(data = output_global, var_ib = paste0("ib_", m))
  assign(paste0("table_masse_", m), table)  
}

table = cbind(obs, table_masse_MNL_2, table_masse_MNL_3, table_masse_BG_1, table_masse_MS_1)
colnames(table) = c('Observed', "MNL\\_2", "MNL\\_3", "BG\\_1","MS\\_1" )
rownames(table) = c("Masse totale 2011-2015 (en 1e6)", "Masse totale 2012 (en 1e6)",  "Masse totale 2015 (en 1e6)",
                    "Masse totale 2011-2015 TTH1 (en 1e6)", "Masse totale 2012 TTH1  (en 1e6)",  "Masse totale 2015 TTH1  (en 1e6)",
                    "Masse totale 2011-2015 TTH2 (en 1e6)", "Masse totale 2012 TTH2  (en 1e6)",  "Masse totale 2015 TTH2  (en 1e6)",
                    "Masse totale 2011-2015 TTH3 (en 1e6)", "Masse totale 2012 TTH3  (en 1e6)",  "Masse totale 2015 TTH3  (en 1e6)",
                    "Masse totale 2011-2015 TTH4 (en 1e6)", "Masse totale 2012 TTH4  (en 1e6)",  "Masse totale 2015 TTH4  (en 1e6)"
                      )

print(xtable(table,nrow = nrow(table), 
             ncol=ncol(table_movers)+1, byrow=T, digits = 2),
      sanitize.text.function=identity,size="\\footnotesize", hline.after = c(0, 3, 6, 9, 12, 15),
      only.contents=F, include.colnames = T)



table_gain_ib = function(data, var_ib, var_situation)
{
  data$var_ib = data[, var_ib]
  data$var_situation = data[, var_situation]
  data$next_ib = ave(data$var_ib, data$ident, FUN = shift1)
  data$gain_ib = data$next_ib - data$var_ib
  data$I_gain = ifelse(data$gain_ib >0, 1, 0)
  data$gain_ib_pct = 100*(data$gain_ib)/data$var_ib
  data = data[which(data$annee < 2015),]
  
  table = numeric(21)
  
  table[1] = mean(data$gain_ib, na.rm = T)
  table[2] = median(data$gain_ib_pct, na.rm = T)
  table[3] = 100*mean(data$I_gain, na.rm = T)
  
  list_grade = c("TTH1", "TTH2", "TTH3", "TTH4")
  for (g in 1:length(list_grade))
  {
    list = which(data$c_cir_2011 == list_grade[g])
    table[3*g+1] = mean(data$gain_ib[list], na.rm = T)
    table[3*g+2] = median(data$gain_ib_pct[list], na.rm = T)
    table[3*g+3] = 100*mean(data$I_gain[list], na.rm = T)
  }
  list = which(data$var_situation == "no_exit")
  table[16] = mean(data$gain_ib[list], na.rm = T)
  table[17] = 100*mean(data$I_gain[list], na.rm = T)
  list = which(data$var_situation == "exit_next")
  table[18] = mean(data$gain_ib[list], na.rm = T)
  table[19] = 100*mean(data$I_gain[list], na.rm = T)
  list = which(data$var_situation == "exit_oth")
  table[20] = mean(data$gain_ib[list], na.rm = T)
  table[21] = 100*mean(data$I_gain[list], na.rm = T)
  
  return(table)
}

obs = table_gain_ib(output_global, "ib", "situation")
for (m in c("MNL_1","MNL_2", "MNL_3", "BG_1","MS_1" ))
{
  table = table_gain_ib(data = output_global, var_ib = paste0("ib_", m) , paste0("situation_", m) )
  assign(paste0("table_gain_", m), table)  
}

table = cbind(obs, table_gain_MNL_2, table_gain_MNL_3, table_gain_BG_1, table_gain_MS_1)
colnames(table) = c('Observed', "MNL\\_2", "MNL\\_3", "BG\\_1","MS\\_1" )
rownames(table) = c("gain ib moyen", "gain ib median en \\%", "\\% gain ib > 0",
                     "gain ib moyen TTH1", "gain ib median en \\% TTH1", "\\% gain ib > 0  TTH1",
                     "gain ib moyen TTH2", "gain ib median en \\% TTH2", "\\% gain ib > 0  TTH2",
                     "gain ib moyen TTH3", "gain ib median en \\% TTH3", "\\% gain ib > 0 TTH3",
                     "gain ib moyen TTH4", "gain ib median en \\% TTH4", "\\% gain ib > 0 TTH4",
                     "gain ib moyen no\\_exit", "\\% gain ib > 0 no\\_exit",
                     "gain ib moyen exit\\_next", "\\% gain ib > 0 exit\\_next",
                     "gain ib moyen exit\\_oth", "\\% gain ib > 0 exit\\_oth"
                     )

print(xtable(table,nrow = nrow(table), align = "l|c|cccc",
             ncol=ncol(table_movers)+1, byrow=T, digits = 2),
      sanitize.text.function=identity,size="\\footnotesize", hline.after = c(0, 3, 6, 9, 12, 15, 17, 19, 21),
      only.contents=F, include.colnames = T)


check_old = table

