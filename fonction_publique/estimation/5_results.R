

#################################  Simulation diagnosis ###############################
# Comparing predicted and observed outcomes 
# I.  Tests for 2011
  # 1. Exit
  # 2. Predicted ib
# II. Dynamics of grade exit 2011-2014
 

## I. 2011 ####

## 1. Load data

# Observed data
data_obs <- read.csv(paste0(data_path, 'data_ATT_2002_2015_with_filter_on_etat_at_exit_and_change_to_filter_on_etat_grade_corrected.csv'))
to_bolean = c("left_censored", "exit_status")
data_obs[, to_bolean] <- sapply(data_obs[, to_bolean], as.logical)

data_obs1 <- subset(data_obs, annee == 2012 & left_censored == F, 
                      select = c("ident", "c_cir", "echelon", "ib", "sexe", "generation",  "exit_status"))
setnames(data_obs1, old = c("ident", "c_cir", "echelon", "ib"), 
                    new = c('ident', 'grade_2012_obs', 'echelon_2012_obs', 'ib_2012_obs'))
data_obs2 <- subset(data_obs, annee == 2011 & left_censored == F, select=c("c_cir", "echelon", "ib"))
setnames(data_obs2, old = c("c_cir", "echelon", "ib"), 
                    new = c('grade_2011_obs', 'echelon_2011_obs', 'ib_2011_obs'))
data = cbind(data_obs1, data_obs2)

data$situation_2012_obs = ifelse(data$exit_status == 0, "no_exit", "exit_oth")
data$situation_2012_obs[which(data$exit_status == 1 & data$grade_2011_obs == "TTH1" & data$grade_2012_obs == "TTH2")] = "exit_next"
data$situation_2012_obs[which(data$exit_status == 1 & data$grade_2011_obs == "TTH2" & data$grade_2012_obs == "TTH3")] = "exit_next"
data$situation_2012_obs[which(data$exit_status == 1 & data$grade_2011_obs == "TTH3" & data$grade_2012_obs == "TTH4")] = "exit_next"

# Correction temporaire
data = data[which(data$echelon_2011_obs != 55555),]
data= setorder(data, ident)

# Simul ib from python
model_names <- c("_m1", "_m2", "_m3")
for (i in model_names)
{
  pred <- read.csv(paste0(asset_simulation_path, 'results_modif_regles_replacement/', 'results_2011', i, '.csv'))
  pred <- setorder(pred, ident)
  # Check: 
  if (length(which(pred$ident!=data$ident))!=0){print("Pbl: appending different ind"); stop()}
  add <- subset(pred, select=c("grade", "echelon", "ib", "situation"))
  colnames(add) <- c(paste0(c('grade_2012', 'echelon_2012', 'ib_2012', 'situation_2012'), i))
  data <- cbind(data, add)
}


## 2. Exit 


# ROC analysis
exit = as.matrix(data[, c("situation_2012_obs", paste0("situation_2012", model_names))])
table_fit = matrix(ncol = length(model_names), nrow = 9)
for (m in 1:length(model_names))
{
  c = m+1
  table_fit[1, m] =  100*length(which(exit[,c] == "no_exit"))/length(exit[,c])
  table_fit[2, m] =   table_fit[1, m]-100*(length(which(exit[,1] == "no_exit"))/length(exit[,1]))
  table_fit[3, m] = 100*length(which(exit[,c] == "exit_next"))/length(exit[,c])
  table_fit[4, m] =   table_fit[3, m]-100*(length(which(exit[,1] == "exit_next"))/length(exit[,1]))
  table_fit[5, m] = 100*length(which(exit[,c] == "exit_oth"))/length(exit[,c])
  table_fit[6, m] =   table_fit[5, m]-100*(length(which(exit[,1] == "exit_oth"))/length(exit[,1]))
  table_fit[7, m] = 100*length(which(exit[,c] == "no_exit" & exit[,1] == "no_exit"))/length(which(exit[,1] == "no_exit"))
  table_fit[8, m] = 100*length(which(exit[,c] == "exit_next" & exit[,1] == "exit_next"))/length(which(exit[,1] == "exit_next"))
  table_fit[9, m] = 100*length(which(exit[,c] == "exit_oth" & exit[,1] == "exit_oth"))/length(which(exit[,1] == "exit_oth"))
}  
  
colnames(table_fit) = model_names
rownames(table_fit) = c("Prop of no exit", "Diff with no exit obs", 
                        "Prop of exit next", "Diff with exit next", 
                        "Prop of exit oth", "Diff with exit oth", 
                        "\\% good pred when obs = no exit", 
                        "\\% good pred when obs = exit next",
                        "\\% good pred when obs = exit oth")

mdigit <- matrix(c(rep(0,(ncol(table_fit)+1)*2),rep(3,(ncol(table_fit)+1)*6)),nrow = nrow(table_fit), ncol=ncol(table_fit)+1, byrow=T)
print(xtable(table_fit,nrow = nrow(table_fit), ncol=ncol(table_fit)+1, byrow=T, digits = 2),
      sanitize.text.function=identity,size="\\footnotesize", hline.after = c(0, 2, 4, 6),
      only.contents=F, include.colnames = T)

# Caracteristics of movers
data$age = 2011 - data$generation
data$femme =ifelse(data$sexe == "F", 1, 0)

table_movers = matrix(ncol = length(model_names)+1, nrow = 20)
for (c in 1:4)
{
  # All
  table_movers[1,c] = 100*length(which(exit[, c] == "exit_next"))/length(exit[,c])
  table_movers[2,c] = 100*length(which(exit[, c] == "exit_oth"))/length(exit[,c])                              
  # Women
  list = which(data$femme == 1)
  table_movers[3,c] = 100*length(which(exit[list, c] == "exit_next"))/length(exit[list,c])
  table_movers[4,c] = 100*length(which(exit[list, c] == "exit_oth"))/length(exit[list,c])  
  # TTH1
  list = which(data$grade_2011 == "TTH1")
  table_movers[5,c] = 100*length(which(exit[list, c] == "exit_next"))/length(exit[list,c])
  table_movers[6,c] = 100*length(which(exit[list, c] == "exit_oth"))/length(exit[list,c])  
  # TTH2
  list = which(data$grade_2011 == "TTH2")
  table_movers[7,c] = 100*length(which(exit[list, c] == "exit_next"))/length(exit[list,c])
  table_movers[8,c] = 100*length(which(exit[list, c] == "exit_oth"))/length(exit[list,c])  
  # TTH3
  list = which(data$grade_2011 == "TTH3")
  table_movers[9,c] = 100*length(which(exit[list, c] == "exit_next"))/length(exit[list,c])
  table_movers[10,c] = 100*length(which(exit[list, c] == "exit_oth"))/length(exit[list,c])  
  # TTH4
  list = which(data$grade_2011 == "TTH4")
  table_movers[11,c] = 100*length(which(exit[list, c] == "exit_next"))/length(exit[list,c])
  table_movers[12,c] = 100*length(which(exit[list, c] == "exit_oth"))/length(exit[list,c])  
  # IB distrib
  list = which(exit[, c] == "exit_next")
  table_movers[13,c] = mean(data$ib_2011[list])
  table_movers[14:16,c] = as.numeric(quantile(data$ib_2011_obs[list])[2:4])
  list = which(exit[, c] == "exit_oth")
  table_movers[17,c] = mean(data$ib_2011[list])
  table_movers[18:20,c] = as.numeric(quantile(data$ib_2011_obs[list])[2:4])
}  

colnames(table_movers) = c('Observed', model_names)
rownames(table_movers) = c("\\% exit next All", "\\% exit oth All", "\\% exit next Women", "\\% exit oth Women",
                           "\\% exit next TTH1", "\\% exit oth TTH1", "\\% exit next TTH2", "\\% exit oth TTH2",
                           "\\% exit next TTH3", "\\% exit oth TTH3", "\\% exit next TTH4", "\\% exit oth TTH4",
                           "Mean IB when exit next", "Q1 IB when exit next", "Q2 IB when exit next","Q3 IB when exit next",
                           "Mean IB when exit oth", "Q1 IB when exit oth", "Q2 IB when exit oth","Q3 IB when exit oth")


mdigit <- matrix(c(rep(2,(ncol(table_movers)+1)*12),rep(0,(ncol(table_movers)+1)*8)),
                 nrow = nrow(table_movers), ncol=ncol(table_movers)+1, byrow=T)                           
print(xtable(table_movers,nrow = nrow(table_movers), 
             ncol=ncol(table_movers)+1, byrow=T, digits = mdigit),
      sanitize.text.function=identity,size="\\footnotesize", hline.after = c(0, 2, 4, 6, 8, 10, 12, 16),
      only.contents=F, include.colnames = T)



## 3. IB 2012 ##
ib2012 = as.matrix(data[, c("ib_2012_obs", paste0("ib_2012", model_names))])
# Masse ib
wage_bill = matrix(ncol = length(model_names)+1, nrow = 16)
for (c in 1:4)
{
  # All
  wage_bill[1,c] = sum(ib2012[,c])/1e6
  wage_bill[2,c] = (sum(ib2012[,c])/1e6-sum(ib2012[,1])/1e6)/(sum(ib2012[,1])/1e6)                          
  # TTH1
  list = which(data$grade_2011 == "TTH1")
  wage_bill[3,c] = sum(ib2012[list ,c])/1e6
  wage_bill[4,c] = (sum(ib2012[list,c])/1e6-sum(ib2012[list,1])/1e6)/(sum(ib2012[list,1])/1e6)  
  # TTH2
  list = which(data$grade_2011 == "TTH2")
  wage_bill[5,c] = sum(ib2012[list ,c])/1e6
  wage_bill[6,c] = (sum(ib2012[list,c])/1e6-sum(ib2012[list,1])/1e6)/(sum(ib2012[list,1])/1e6)  
  # TTH3
  list = which(data$grade_2011 == "TTH3")
  wage_bill[7,c] = sum(ib2012[list ,c])/1e6
  wage_bill[8,c] = (sum(ib2012[list,c])/1e6-sum(ib2012[list,1])/1e6)/(sum(ib2012[list,1])/1e6)  
  # TTH4
  list = which(data$grade_2011 == "TTH4")
  wage_bill[9,c] = sum(ib2012[list ,c])/1e6
  wage_bill[10,c] = (sum(ib2012[list,c])/1e6-sum(ib2012[list,1])/1e6)/(sum(ib2012[list,1])/1e6)  
  # By next year
  list = which(data$situation_2012_obs == "no_exit")
  wage_bill[11,c] = sum(ib2012[list ,c])/1e6
  wage_bill[12,c] = (sum(ib2012[list,c])/1e6-sum(ib2012[list,1])/1e6)/(sum(ib2012[list,1])/1e6)  
  list = which(data$situation_2012_obs == "exit_next")
  wage_bill[13,c] = sum(ib2012[list ,c])/1e6
  wage_bill[14,c] = (sum(ib2012[list,c])/1e6-sum(ib2012[list,1])/1e6)/(sum(ib2012[list,1])/1e6)  
  list = which(data$situation_2012_obs == "exit_oth")
  wage_bill[15,c] = sum(ib2012[list ,c])/1e6
  wage_bill[16,c] = (sum(ib2012[list,c])/1e6-sum(ib2012[list,1])/1e6)/(sum(ib2012[list,1])/1e6)  
}  

colnames(table_movers) = c('Observed', model_names)
rownames(table_movers) = c("\\% exit next All", "\\% exit oth All", "\\% exit next Women", "\\% exit oth Women",
                           "\\% exit next TTH1", "\\% exit oth TTH1", "\\% exit next TTH2", "\\% exit oth TTH2",
                           "\\% exit next TTH3", "\\% exit oth TTH3", "\\% exit next TTH4", "\\% exit oth TTH4",
                           "Mean IB when exit next obs", "Q1 IB when exit next obs", "Q2 IB when exit next obs","Q3 IB when exit next obs",
                           "Mean IB when exit oth obs", "Q1 IB when exit oth obs", "Q2 IB when exit oth obs","Q3 IB when exit oth obs")

mdigit <- matrix(c(rep(2,(ncol(table_movers)+1)*12),rep(0,(ncol(table_movers)+1)*8)),
                 nrow = nrow(table_movers), ncol=ncol(table_movers)+1, byrow=T)                           
print(xtable(table_movers,nrow = nrow(table_movers), 
             ncol=ncol(table_movers)+1, byrow=T, digits = mdigit),
      sanitize.text.function=identity,size="\\footnotesize", hline.after = c(0, 2, 4, 6, 8, 10, 12, 16),
      only.contents=F, include.colnames = T)

# Distributions
ncolors = c("red", "darkcyan", "blue", "black")
plot (density(as.numeric(ib2012[,1])), col =  ncolors[1], xlim = c(275, 450),
      main = "Distribution des IB en 2012")
for (c in 2:ncol(ib2012)){lines (density(as.numeric(ib2012[,c])), col = ncolors[c])}

plot (density(as.numeric(ib2012[which(exit[,1]=="no_exit"),1])), col =  ncolors[1], xlim = c(275, 450), 
      main = "Distribution des IB en 2012 (pas de changement de grade)")
for (c in 2:ncol(ib2012)){lines (density(as.numeric(ib2012[which(exit[,c]=="no_exit"),c])), col = ncolors[c])}

plot (density(as.numeric(ib2012[which(exit[,1]!="no_exit"),1])), col =  ncolors[1], xlim = c(275, 450), 
      main = "Distribution des IB en 2012 (changement de grade)")
for (c in 2:ncol(ib2012)){lines (density(as.numeric(ib2012[which(exit[,c]!="no_exit"),c])), col = ncolors[c])}

# Variation d'IB
var_ib2012 = (ib2012 - data$ib_2011_obs)/data$ib_2011_obs
var_ib = matrix(ncol = length(model_names)+1, nrow = 11)
for (c in 1:4)
{
  # All
  var_ib[1,c] = mean(100*var_ib2012[,c])
  # TTH1
  list = which(data$grade_2011 == "TTH1")
  var_ib[2,c] = mean(100*var_ib2012[list ,c])
  # TTH2
  list = which(data$grade_2011 == "TTH2")
  var_ib[3,c] = mean(100*var_ib2012[list ,c])
  # TTH3
  list = which(data$grade_2011 == "TTH3")
  var_ib[4,c] = mean(100*var_ib2012[list ,c])
  # TTH4
  list = which(data$grade_2011 == "TTH4")
  var_ib[5,c] = mean(100*var_ib2012[list ,c])
  # By (predicted) next year
  list = which(exit[,c] == "no_exit")
  var_ib[6,c] = mean(100*var_ib2012[list ,c])
  var_ib[7,c] = median(100*var_ib2012[list ,c])
  list = which(exit[,c] == "exit_next")
  var_ib[8,c] = mean(100*var_ib2012[list ,c])
  var_ib[9,c] = median(100*var_ib2012[list ,c])
  list = which(exit[,c] == "exit_oth")
  var_ib[10,c] = mean(100*var_ib2012[list ,c])
  var_ib[11,c] = median(100*var_ib2012[list ,c])
}  

colnames(var_ib) = c('Observed', model_names)
rownames(var_ib) = c("mean \\% increase IB All",
                      "mean \\% increase IB TTH1", "mean \\% increase IB TTH2", 
                      "mean \\% increase IB TTH3", "mean \\% increase IB TTH4",
                      "mean\\% increase IB for when no exit", "median\\% increase IB for when no exit",
                      "mean\\% increase IB for when exit next", "median\\% increase IB for when exit next",
                      "mean\\% increase IB for when exit oth", "median\\% increase IB for when exit oth")

mdigit <- matrix(c(rep(2,(ncol(table_movers)+1)*12),rep(0,(ncol(table_movers)+1)*8)),
                 nrow = nrow(table_movers), ncol=ncol(table_movers)+1, byrow=T)                           
print(xtable(table_movers,nrow = nrow(table_movers), 
             ncol=ncol(table_movers)+1, byrow=T, digits = mdigit),
      sanitize.text.function=identity,size="\\footnotesize", hline.after = c(0, 2, 4, 6, 8, 10, 12, 16),
      only.contents=F, include.colnames = T)



## II. Exit grade 2011-2014 ####
data_exit = load(paste0(save_data_path, "data_simul1.Rdata"))



## Survival curve
survival= function(sample, type_exit = "all", save = F, name = "")
{
  years = 2011:2015
  surv  = matrix(ncol = 5, nrow = 4)  
  list = sample
  for (y in 1:length(years))
  {
    n = length(list)
    surv[1, y] = (n - length(which(exit_year_obs[list] < years[y])))/n
    surv[2, y] = (n - length(which(exit_year_pred[1, list]  < years[y])))/n
    surv[3, y] = (n - length(which(exit_year_pred[2, list]  < years[y])))/n
    surv[4, y] = (n - length(which(exit_year_pred[3, list]  < years[y])))/n  
  }
  # Plot
  
  colors = c("black", "darkcyan")
  limits = range(surv)
  plot(years,rep(NA,length(years)),ylim=limits, ylab="Survie dans le grade",xlab="Année")
  title(name)
  lines(years, surv[1,], col =  colors[1], lwd = 3, lty =1)
  lines(years, surv[2,], col =  colors[2], lwd = 3, lty = 2)
  lines(years, surv[3,], col =  colors[2], lwd = 4, lty = 3)
  lines(years, surv[4,], col =  colors[2], lwd = 4, lty =1)
  legend("topright", legend = c("Obs", "m0", "m1", "m2"), col = c(colors[1], rep(colors[2], 3)), lty = c(1,2,3,1), lwd = 3)
}

datai= data_sim[which(data_sim$annee == 2011),]
survival(sample = 1:ncol(exit_year_pred), type_exit = "all", save = F, name = "Tous")

par(mfrow=c(2,2))
survival(sample = which(datai$c_cir_2011 == "TTH1"), type_exit = "all", save = F, name = "TTH1")
survival(sample = which(datai$c_cir_2011 == "TTH2"), type_exit = "all", save = F, name = "TTH2")
survival(sample = which(datai$c_cir_2011 == "TTH3"), type_exit = "all", save = F, name = "TTH3")
survival(sample = which(datai$c_cir_2011 == "TTH4"), type_exit = "all", save = F, name = "TTH4")



hazard= function(sample, type_exit = "all", save = F, name = "")
{
  haz  = matrix(ncol = 4, nrow = 4)  
  list = sample
  years = 2011:2014
  
  if (!is.element(type_exit, c("all", "exit_next", "exit_oth"))){print("wrong exit type"); return()}
  
  # All
  if (type_exit == "all")
  {
    for (y in 1:length(years))
    {
      n = length(list)
      haz[1, y] =  length(which(exit_year_obs[list] == years[y]))/length(which(exit_year_obs[list] >= years[y]))
      haz[2, y] =  length(which(exit_year_pred[1, list] == years[y]))/length(which(exit_year_pred[1, list] >= years[y]))
      haz[3, y] =  length(which(exit_year_pred[2, list] == years[y]))/length(which(exit_year_pred[2, list]  >= years[y]))
      haz[4, y] =  length(which(exit_year_pred[3, list] == years[y]))/length(which(exit_year_pred[3, list ] >= years[y]))
    }
  }
  else{
    for (y in 1:length(years))
    {
      n = length(list)
      haz[1, y] =  length(which(exit_year_obs[list] == years[y] & exit_route_obs[list] == type_exit))/length(which(exit_year_obs[list] >= (years[y])))
      haz[2, y] =  length(which(exit_year_pred[1, list] == years[y] & exit_route_pred[1,list] == type_exit))/length(which(exit_year_pred[1, list] >= years[y])) 
      haz[3, y] =  length(which(exit_year_pred[2, list] == years[y] & exit_route_pred[2,list] == type_exit))/length(which(exit_year_pred[2, list] >= years[y]))
      haz[4, y] =  length(which(exit_year_pred[3, list] == years[y] & exit_route_pred[3,list] == type_exit))/length(which(exit_year_pred[3, list] >= years[y]))
    }
    
  }
  
  # Plot
  years = 2012:2015
  colors = c("black", "darkcyan")
  limits = range(haz)
  plot(years,rep(NA,length(years)),ylim=limits, ylab="Hazard rate",xlab="Année")
  title(name)
  lines(years, haz[1,], col =  colors[1], lwd = 3, lty =1)
  lines(years, haz[2,], col =  colors[2], lwd = 3, lty = 2)
  lines(years, haz[3,], col =  colors[2], lwd = 4, lty = 3)
  lines(years, haz[4,], col =  colors[2], lwd = 4, lty =1)
}


hazard(sample = 1:ncol(exit_year_pred), type_exit = "all",       save = F, name = "All")
hazard(sample = 1:ncol(exit_year_pred), type_exit = "exit_next", save = F, name = "Next grade")
hazard(sample = 1:ncol(exit_year_pred), type_exit = "exit_oth",  save = F, name = "Exit corps")


hazard(sample = which(datai$c_cir == "TTH1"), type_exit = "all",       save = F, name = "All exits, TTH1")
hazard(sample = which(datai$c_cir == "TTH1"), type_exit = "exit_next", save = F, name = "Next grade, TTH1")
hazard(sample = which(datai$c_cir == "TTH1"), type_exit = "exit_oth",  save = F, name = "Next grade, TTH1")


hazard(sample = which(datai$c_cir == "TTH2"), type_exit = "all",       save = F, name = "All exits, TTH2")
hazard(sample = which(datai$c_cir == "TTH3"), type_exit = "all",       save = F, name = "All exits, TTH3")
hazard(sample = which(datai$c_cir == "TTH4"), type_exit = "all",       save = F, name = "All exits, TTH4")


hazard(sample = which(datai$c_cir == "TTH2"), type_exit = "exit_next", save = F, name = "Next grade")
hazard(sample = which(datai$c_cir == "TTH3"), type_exit = "exit_next", save = F, name = "Next grade")
hazard(sample = which(datai$c_cir == "TTH4"), type_exit = "exit_next", save = F, name = "Next grade")

hazard(sample = 1:ncol(exit_year_pred), type_exit = "exit_oth",  save = F, name = "All")






