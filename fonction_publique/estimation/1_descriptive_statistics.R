
library(xtable)



######## Descriptive statistics ########


source(paste0(wd, "0_work_on_data.R"))
datasets = load_and_clean(data_path, "/data_ATT_2002_2015_with_filter_on_etat_at_exit_and_change_to_filter_on_etat_grade_corrected.csv")
data_id = datasets[[1]]
data_max = datasets[[2]]
data_min = datasets[[3]]


data_stat = data_min[which(data_min$left_censored == F),]
datai   =  data_id[which(data_id$left_censored == F),]


####### I. Sample description #######

## I.1 Sample  ####
table_count <- matrix(ncol = 5, nrow = 2)
table_count[1,1] <- length(unique(data_id$ident))
table_count[2,1] <- 100
table_count[1,2:5] <- format(round(as.data.frame(table(data_id$c_cir_2011))[1:4,2]))
table_count[2, 2:5] <- format(round(as.data.frame(table(data_id$c_cir_2011))[1:4,2]/length(unique(data_id$ident))*100,1),1)
colnames(table_count) = c("All", "TTH1","TTH2", "TTH3", "TTH4")
rownames(table_count) = c('\\Number of agents', "\\% share of ATT population")

print(xtable(table_count,align="lccccc",nrow = nrow(table), ncol=ncol(table_censoring)+1, byrow=T, digits = 3),
      sanitize.text.function=identity,size="\\footnotesize", 
      only.contents=F, include.colnames = T)

data <- read.csv(paste0("M:/CNRACL/output/clean_data_finalisation", "/data_ATT_2002_2015_2.csv"))
data_id_bis <- data[!duplicated(data[,"ident"]),]
table_count_grade_next = matrix(ncol = 6, nrow = 2)
table_count_grade_next[1,1] = length(unique(data_id_bis$ident))
table_count_grade_next[2,1] = 100
table_count_grade_next[1,2:6] = format(round(as.data.frame(table(data_id_bis$grade_bef))[1:5,2]))
table_count_grade_next[2, 2:6] = format(round(as.data.frame(table(data_id_bis$grade_bef))[1:5,2]/length(unique(data_id_bis$ident))*100,1),1)
colnames(table_count_grade_next) = c("All", "missing", "other", "TTH1","TTH2", "TTH3")
rownames(table_count_grade_next) = c('\\Number of agents', "\\% share of ATT population")

data_1st_y <- data[which(data$annee == data$last_y_in_grade_bef),]
data_1st_y_autre <- data_1st_y[which(data_1st_y$c_cir == "autre"),]
data_1st_y_autre_ib_null <- data_1st_y[which(data_1st_y$ib == 0),]
print(dim(data_1st_y_autre_ib_null))

data_last_y <- data[which(data$annee == data$first_y_in_next_grade),]

print(xtable(table_count_grade_next,align="lcccccc",nrow = nrow(table), ncol=ncol(table_count_grade_next)+1, byrow=T, digits = 3),
      sanitize.text.function=identity,size="\\footnotesize", 
      only.contents=F, include.colnames = T)

table_count_grade_next = matrix(ncol = 6, nrow = 2)
table_count_grade_next[1,1] = length(unique(data$ident))
table_count_grade_next[2,1] = 100
table_count_grade_next[1,2:6] = format(round(as.data.frame(table(data$grade_bef))[1:5,2]))
table_count_grade_next[2, 2:6] = format(round(as.data.frame(table(data$grade_bef))[1:5,2]/length(unique(data$ident))*100,1),1)
colnames(table_count_grade_next) = c("All", "missing", "other", "TTH1","TTH2", "TTH3")
rownames(table_count_grade_next) = c('\\Number of agents', "\\% share of ATT population")

print(xtable(table_count_grade_next,align="lcccccc",nrow = nrow(table), ncol=ncol(table_count_grade_next)+1, byrow=T, digits = 3),
      sanitize.text.function=identity,size="\\footnotesize", 
      only.contents=F, include.colnames = T)

## I.2 Censoring ####

data_id$right = as.numeric(data_id$right_censored)
data_id$left = as.numeric(data_id$left_censored)

mean_right <- aggregate(data_id$right, by = list(data_id$c_cir_2011), FUN=mean)    
mean_left  <- aggregate(data_id$left,  by = list(data_id$c_cir_2011), FUN=mean)    

table_censoring = matrix(ncol = 5, nrow = 2)
table_censoring[1,1] = mean(data_id$right)
table_censoring[1,2:5] = mean_right$x
table_censoring[2,1] = mean(data_id$left)
table_censoring[2,2:5] = mean_left$x

colnames(table_censoring) = c("All", "TTH1","TTH2", "TTH3", "TTH4")
rownames(table_censoring) = c('\\% right-censored', "\\% left-censored")

print(xtable(table_censoring,align="lccccc",nrow = nrow(table), ncol=ncol(table_censoring)+1, byrow=T, digits = 3),
      sanitize.text.function=identity,size="\\footnotesize", 
      only.contents=F, include.colnames = T)




####### II. Hazard and surival analysis #######


# II.1 Exit analysis ####

extract_exit = function(data, exit_var)
{
  data = data[, c("ident", "annee", "c_cir_2011", exit_var)]
  
  data$exit_var = data[, exit_var]
  data$ind_exit      = ifelse(data$exit_var != "no_exit", 1, 0) 
  data$ind_exit_cum  = ave(data$ind_exit, data$ident, FUN = cumsum)
  data$ind_exit_cum2  = ave(data$ind_exit_cum, data$ident, FUN = cumsum)
  data$ind_exit_cum2  = ave(data$ind_exit_cum, data$ident, FUN = cumsum)
  data$ind_exit_tot   = ave(data$ind_exit, data$ident, FUN = sum)
  ### PB  
  data$ind_first_exit  = ifelse(data$ind_exit_cum2 == 1, 1, 0) 
  data$year_exit = ave((data$ind_first_exit*data$annee), data$ident, FUN = max)
  data$year_exit[which(data$year_exit == 0)] = 2014
  data2 = data[which(data$annee == data$year_exit ),]
  data2$year_exit[which(data2$ind_exit_tot == 0)] = 9999
  
  data2 = data2[, c("ident", "c_cir_2011", "year_exit", "exit_var")]
  return(data2)
}  

compute_hazard= function(data, list, type_exit = "all")
{
  years = 2011:2014
  haz  = numeric(length(years))
  if (!is.element(type_exit, c("all", "exit_next", "exit_oth"))){print("wrong exit type"); return()}
  n = length(list)
  if (type_exit == "all")
  {
    for (y in 1:length(years)){
      haz[y] =  length(which(data$year_exit[list] == years[y]))/
        length(which(data$year_exit[list] >= years[y]))
    }
  }
  else{
    for (y in 1:length(years))
    {
      haz[y] =  length(which(data$year_exit[list] == years[y] & data$exit_var[list] == type_exit))/
        length(which(data$year_exit[list] >= (years[y])))
    }
  }
  return(haz)  
}

plot_hazards = function(hazard, colors, type, title)
{
  years = 2011:2014
  limits = c(0, max(hazard))
  plot(years,rep(NA,length(years)),ylim=limits, ylab="Hazard rate",xlab="Année")
  title(title)
  for (l in 1:nrow(hazard)){lines(years, hazard[l,], col =  colors[l], lwd = 3, lty = types[l])}  
}

data = extract_exit(data_stat, "next_year")

list_TTH1 = which(datai$c_cir_2011 == "TTH1")
list_TTH2 = which(datai$c_cir_2011 == "TTH2")
list_TTH3 = which(datai$c_cir_2011 == "TTH3")
list_TTH4 = which(datai$c_cir_2011 == "TTH4")

list_G1 = which(datai$generation_group == 6)
list_G2 = which(datai$generation_group == 7)
list_G3 = which(datai$generation_group == 8)

types = c(1, 1, 2)
routes = c("all", "exit_next", "exit_oth")
colors = c("black", "darkcyan", "darkcyan")
### All
list = 1:length(data$ident)
haz = matrix(ncol= length(2011:2014), nrow = 3)
for (t in 1:length(routes)){haz[t,] = compute_hazard(data, list, type = routes[t])}
plot_hazards(haz, colors, types, title = "Tous")

### TTH1
list = list_TTH1
haz = matrix(ncol= length(2011:2014), nrow = 3)
for (t in 1:length(routes)){haz[t,] = compute_hazard(data, list, type = routes[t])}
plot_hazards(haz, colors, types, title = "TTH1")
### TTH2
list = list_TTH2
haz = matrix(ncol= length(2011:2014), nrow = 3)
for (t in 1:length(routes)){haz[t,] = compute_hazard(data, list, type = routes[t])}
plot_hazards(haz, colors, types, title = "TTH2")
### TTH3
list = list_TTH3
haz = matrix(ncol= length(2011:2014), nrow = 3)
for (t in 1:length(routes)){haz[t,] = compute_hazard(data, list, type = routes[t])}
plot_hazards(haz, colors, types, title = "TTH3")
### TTH4
list = list_TTH4
haz = matrix(ncol= length(2011:2014), nrow = 3)
for (t in 1:length(routes)){haz[t,] = compute_hazard(data, list, type = routes[t])}
plot_hazards(haz, colors, types, title = "TTH4")


# II.2 Effect of institutional threshold ####


### II.1 Functions ####

# Hazard by duration in grade
hazard_by_duree = function(data, save = F, corps = F, type_exit = "")
{
  grade = seq(1, 12)
  hazard   = numeric(length(grade))
  effectif = numeric(length(grade))
  
  data$exit = data$exit_status2
  if (type_exit == "in_corps") {data$exit[which(data$next_year == "exit_oth")] = 0}
  if (type_exit == "out_corps"){data$exit[which(data$next_year == "exit_next")] = 0}
  
  for (g in 1:length(grade))
  {
  hazard[g]   = length(which(data$time ==  grade[g] & data$exit == 1))/length(which(data$time == grade[g]))
  effectif[g] = length(which(data$time == grade[g]))
  }  
  par(mar = c(5,5,2,5))
  xlabel = ifelse(corps, "Duration in section", "Duration in rank")
  plot(grade, hazard, type ="l", lwd = 3, xlab = xlabel, ylab = "Hazard rate", col = "darkcyan")
  par(new = T)
  plot(grade, effectif, type ="l", lty = 2, lwd = 2, axes=F, xlab=NA, ylab=NA)
  axis(side = 4)
  mtext(side = 4, line = 3, 'Nb obs.')
  legend("topleft", legend = c("Hazard", "Nb obs."), lwd = 3, lty = c(1,3), col = c("darkcyan", "black"), cex = 1.1)
}  

# Hazard by echelon
hazard_by_ech = function(data, save = F, type_exit = "")
{
  ech = 1:12
  hazard = numeric(length(ech))
  effectif = numeric(length(ech))
  
  data$exit = data$exit_status2
  if (type_exit == "in_corps") {data$exit[which(data$next_year == "exit_oth")] = 0}
  if (type_exit == "out_corps"){data$exit[which(data$next_year == "exit_next")] = 0}
  
  
  for (e in 1:length(ech))
  {
  hazard[e] =   length(which(data$echelon == ech[e] & data$exit == 1))/length(which(data$echelon == ech[e]))
  effectif[e] = length(which(data$echelon == ech[e]))
  }  

  par(mar = c(5,5,2,5))
  plot(ech, hazard, type ="l", lwd = 3, xlab = "Level", ylab = "Hazard rate", col = "darkcyan")
  par(new = T)
  plot(ech, effectif, type ="l", lty = 2, lwd = 2, axes=F, xlab=NA, ylab=NA)
  axis(side = 4)
  mtext(side = 4, line = 3, 'Nb. obs')
  legend("topleft", legend = c("Hazard", "Nb obs."), lwd = 3, lty = c(1,3), col = c("darkcyan", "black"), cex = 1.1)
}  



# Distance to thresholds
hazard_by_distance = function(data, save = F, type = "choix", type_exit = "", colors = c("black", "grey", "darkcyan"))
{
  if (type == "choix"){data$cond_grade = data$D_choice ; data$cond_ech = data$E_choice}
  if (type == "exam") {data$cond_grade = data$D_exam ; data$cond_ech = data$E_exam}
  
  data$exit = data$exit_status2
  if (type_exit == "in_corps") {data$exit[which(data$next_year == "exit_oth")] = 0}
  if (type_exit == "out_corps"){data$exit[which(data$next_year == "exit_next")] = 0}
  
  
  data$dist_grade =  data$time  - data$cond_grade
  data$dist_echelon = data$echelon - data$cond_ech
  data$dist_both = pmin(data$dist_grade, data$dist_echelon)
  
  values = (min(min(data$dist_grade), min(data$dist_echelon), min(data$dist_both)):
              min(max(data$dist_grade), max(data$dist_echelon), max(data$dist_both)))
  hazards = matrix(ncol = length(values), nrow = 3)
  
  for (v in 1:length(values))
  {
    hazards[1,v]  = length(which(data$dist_grade  == values[v] & data$exit == 1))/length(which(data$dist_grade  == values[v]))
    hazards[2,v]  = length(which(data$dist_echelon  == values[v] & data$exit == 1))/length(which(data$dist_echelon  == values[v]))
    hazards[3,v]  = length(which(data$dist_both  == values[v] & data$exit == 1))/length(which(data$dist_both  == values[v]))
  }
  
  limy = c(0, max(hazards, na.rm = T))
  plot(values,rep(NA,length(values)),ylim=limy,ylab="Hazard rate",xlab="Distance to threshold")
  lines(values, hazards[1,], col = colors[1], lwd = 3, lty = 2)
  lines(values, hazards[2,], col =  colors[2], lwd = 3, lty = 2)
  lines(values, hazards[3,], col =  colors[3], lwd = 4)
  legend("bottomright", legend = c("Rank", "Level", "Both"),lty = c(2,2,1) , col = colors, lwd = 3)
}  


### II.2 Outputs ####


### II.2.1 TTH1 ####
subdata = data_min
subdata = subdata[which(subdata$left_censored == F & subdata$c_cir_2011 == "TTH1"),]
hazard_by_duree(data = subdata)
hazard_by_ech(data = subdata)
hazard_by_distance(data = subdata)

pdf(paste0(fig_path,"hazard_by_duree_TTH1.pdf"))
hazard_by_duree(data = subdata)
abline(v = 3, lwd = 3)
abline(v = 10, lwd = 3)
dev.off()

pdf(paste0(fig_path,"hazard_by_ech_TTH1.pdf"))
hazard_by_ech(data = subdata)
abline(v = 4, lwd = 3)
abline(v = 7, lwd = 3)
dev.off()

# Variantes dur?e aff
subdata2 = subdata
subdata2$time = subdata2$annee - subdata2$an_aff +1
pdf(paste0(fig_path,"hazard_by_duree_TTH1_bis.pdf"))
hazard_by_duree(data = subdata2)
abline(v = 3, lwd = 3)
abline(v = 10, lwd = 3)
dev.off()


### II.2.2 TTH2 ####

subdata = data_min
subdata = subdata[which(subdata$left_censored == F & subdata$c_cir_2011 == "TTH2"),]
hazard_by_duree(data = subdata)
hazard_by_ech(data = subdata)
hazard_by_distance(data = subdata)

pdf(paste0(fig_path,"hazard_by_duree_TTH2.pdf"))
hazard_by_duree(data = subdata)
abline(v = 6, lwd = 3)
dev.off()

pdf(paste0(fig_path,"hazard_by_ech_TTH2.pdf"))
hazard_by_ech(data = subdata)
abline(v = 5, lwd = 3)
dev.off()

# Variantes dur?e aff
subdata2 = subdata
subdata2$time = subdata2$annee - subdata2$an_aff +1
pdf(paste0(fig_path,"hazard_by_duree_TTH2_bis.pdf"))
hazard_by_duree(data = subdata2, corps = T)
abline(v = 6, lwd = 3)
dev.off()
pdf(paste0(fig_path,"hazard_by_dist_TTH2_bis.pdf"))
hazard_by_distance(data = subdata2)
abline(v = 0, lwd = 3)
dev.off()




### II.2.2 TTH3 ####


subdata = data_min
subdata = subdata[which(subdata$left_censored == F & subdata$c_cir_2011 == "TTH3"),]
hazard_by_duree(data = subdata)
hazard_by_duree(data = subdata, type_exit =  "in_corps")
hazard_by_duree(data = subdata, type_exit =  "out_corps")
hazard_by_ech(data = subdata)
hazard_by_ech(data = subdata, type_exit =  "in_corps")
hazard_by_ech(data = subdata, type_exit =  "out_corps")

hazard_by_distance(data = subdata)

pdf(paste0(fig_path,"hazard_by_duree_TTH3.pdf"))
hazard_by_duree(data = subdata)
abline(v = 5, lwd = 3)
dev.off()

pdf(paste0(fig_path,"hazard_by_ech_TTH3.pdf"))
hazard_by_ech(data = subdata)
abline(v = 6, lwd = 3)
dev.off()

pdf(paste0(fig_path,"hazard_by_dist_TTH3.pdf"))
hazard_by_distance(data = subdata)
abline(v = 0, lwd = 3)
dev.off()


### II.2.2 TTH4 ####

subdata = data_min
subdata = subdata[which(subdata$left_censored == F & subdata$c_cir_2011 == "TTH4"),]
hazard_by_duree(data = subdata)
hazard_by_ech(data = subdata)
hazard_by_distance(data = subdata)

pdf(paste0(fig_path,"hazard_by_duree_TTH4.pdf"))
hazard_by_duree(data = subdata)
dev.off()

pdf(paste0(fig_path,"hazard_by_ech_TTH4.pdf"))
hazard_by_ech(data = subdata)
dev.off()


### III. Next grade ###

compute_transitions_next <- function(data, grade)
{
  data = data[which(data$c_cir_2011 == grade & data$annee == 2011),]
  table_exit = numeric(12)
  # % in each possible next_year
  table_exit[1] = round(length(which(data$next_year == "no_exit"))*100/length(data$next_year),2)
  table_exit[2] = round(length(which(data$next_year == "exit_next"))*100/length(data$next_year),2)
  table_exit[3] = round(length(which(data$next_year == "exit_oth"))*100/length(data$next_year),2)
  # From other known neg
  data_exit_oth = data[which(data$next_year == "exit_oth"), ]
  t = as.data.frame(table(data_exit_oth$next_grade)*100/length(data_exit_oth$next_grade))
  t = t[order(-t$Freq),]
  for (n in 1:4){
  table_exit[3+2*n-1] = toString(t[n,1])
  table_exit[3+2*n] = round(t[n,2],2)
  }
  table_exit[12] = length(which(t$Freq >0))
  return(table_exit)
}
  
  
table1 = compute_transitions_next(data_min, "TTH1")
table2 = compute_transitions_next(data_min, "TTH2")
table3 = compute_transitions_next(data_min, "TTH3")
table4 = compute_transitions_next(data_min, grade = "TTH4")
  
table = cbind(table1, table2, table3, table4)

colnames(table) <-  c("TTH1", "TTH2", "TTH3", "TTH4")
rownames(table) <-  c("\\% no exit", "\\% exit next", "\\% exit oth",
                      "\\hfill 1st oth grade ", "\\hfill  \\% 1st oth", 
                      "\\hfill 2nd oth grade ", "\\hfill  \\% 2nd oth", 
                      "\\hfill 3rd oth grade ", "\\hfill  \\% 3rd oth", 
                      "\\hfill 4th oth grade ", "\\hfill  \\% 4th oth", 
                       "Nb oth grades")

as.numeric(table[c(1,2,3,5,7,9,11), ]) <- as.numeric(table[c(1,2,3,5,7,9,11), ])

print(xtable(table),
      sanitize.text.function=identity,size="\\footnotesize")


## IV. Divers ####


##  Grade de destination ####


##  Annee d'affilation ####

subdata = data_id[which(data_id$left_censored == F),]
time = 2001:2011
prop_entry = matrix(ncol = length(time), nrow = 5)
for (t in 1:length(time))
{
  prop_entry[1,t] = length(which(subdata$an_aff == time[t]))/length(subdata$an_aff)  
  prop_entry[2,t] = length(which(subdata$an_aff == time[t] & subdata$c_cir_2011 == "TTH1"))/length(subdata$an_aff[which(subdata$c_cir_2011 == "TTH1")])    
  prop_entry[3,t] = length(which(subdata$an_aff == time[t] & subdata$c_cir_2011 == "TTH2"))/length(subdata$an_aff[which(subdata$c_cir_2011 == "TTH2")])    
  prop_entry[4,t] = length(which(subdata$an_aff == time[t] & subdata$c_cir_2011 == "TTH3"))/length(subdata$an_aff[which(subdata$c_cir_2011 == "TTH3")])    
  prop_entry[5,t] = length(which(subdata$an_aff == time[t] & subdata$c_cir_2011 == "TTH4"))/length(subdata$an_aff[which(subdata$c_cir_2011 == "TTH4")])    
}  

pdf(paste0(fig_path,"distrib_an_aff.pdf"))
layout(matrix(c(1,2,3,4), nrow=2,ncol=2, byrow=TRUE), heights=c(3,3))
par(mar=c(2.5,4.1,1.3,0.2))
barplot(prop_entry[2,],ylab="Proportion d'entrée",xlab="Année", col = "darkcyan", names.arg = time, main = "TTH1")
barplot(prop_entry[3,],ylab="Proportion d'entrée",xlab="Année", col = "darkcyan", names.arg = time, main = "TTH2")
barplot(prop_entry[4,],ylab="Proportion d'entrée",xlab="Année", col = "darkcyan", names.arg = time, main = "TTH3")
barplot(prop_entry[5,],ylab="Proportion d'entrée",xlab="Année", col = "darkcyan", names.arg = time, main = "TTH4")
dev.off()



### Changement indice 
data = data_min[which(data_min$annee <= 2014),]
mean(data$var_ib[which(data$next_year == "no_exit")])
mean(data$var_ib[which(data$next_year == "exit_next")])
mean(data$var_ib[which(data$next_year == "exit_oth")])


### Check tth4 partant avec ib > 7
subdata = data_min[which(data_min$annee == 2011 & data_min$c_cir_2011 == "TTH4" & data_min$next_grade_corrected == "TTM1"  & data_min$exit_status2 ==1 & data_min$echelon >= 6),]

list_ident = unique(subdata$ident)
datasets = read.csv(file = paste0(data_path, "data_ATT_2002_2015_with_filter_on_etat_at_exit_and_change_to_filter_on_etat_grade_corrected.csv"))
data = datasets[which(is.element(datasets$ident, list_ident) & datasets$annee >= 2011),]
table(data$echelon[which(data$annee == 2012)])
