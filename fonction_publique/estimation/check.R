source(paste0(wd, "0_Outils_CNRACL.R"))
datasets = load_and_clean(data_path, "/filter/data_ATT_2011_filtered_after_duration_var_added_new.csv")
data_max = datasets[[1]]
data_min = datasets[[2]]

data_stat_min = data_min[which(data_min$left_censored == F & data_min$annee <= 2014 & data_min$annee >= 2011),]
data_stat_max = data_max[which(data_max$left_censored == F & data_max$annee <= 2014 & data_max$annee >= 2011),]



y = 2011
list1 = data_stat_min$ident[which(data_stat_min$grade == "TTH3" & data_stat_min$grade_next == "TTH4" & data_stat_min$annee == y)]
data_check = data_stat_min[which(is.element(data_stat_min$ident, list1)),]
data_check = data_check[which(data_check$annee == y | data_check$annee == y+1), ]
table(data_check$echelon[which(data_check$annee == y)])
table(data_check$time_spent_in_grade_min[which(data_check$annee == y)])
table(data_check$time_spent_in_grade_max[which(data_check$annee == y)])

echelon = data_check$echelon[which(data_check$annee == y)]
echelon_next = data_check$echelon[which(data_check$annee == y+1)]
plot(echelon, echelon_next)

#### Test thresholds ####
data_check = data_stat_min[which(data_stat_min$c_cir_2011 == "TTH3" & data_stat_min$annee >= 2011),]
data_check = data_stat_max[which(data_stat_max$c_cir_2011 == "TTH3" & data_stat_max$annee >= 2011),]

#  Grade threshold
data_check$grade_cond = 5
data_check$dist_grade_cond = data_check$time - data_check$grade_cond

# Echelon threshold
data_check$ech_cond = 6

grille_ech = data.frame(echelon =  seq(1, 11), duree_min= c(12, 24, 24, 36, 36, 36, 48, 48, 48, 48, 48))
grille_ech$cum_duree = cumsum(grille_ech$duree_min)
grille_ech$dist_duree = grille_ech$cum_duree - 168

data_check = merge(data_check, grille_ech[, c(1,4)], by = "echelon", all.x = T) 
data_check$a = 1
data_check$duree_in_ech = ave(data_check$a, list(data_check$ident, data_check$grade, data_check$echelon), FUN = cumsum)
data_check$dist_ech_cond = (data_check$dist_duree)/12 + data_check$duree_in_ech


data_check$dist_threshold_bef = pmin(0, pmin(data_check$dist_grade_cond, data_check$dist_ech_cond ))
data_check$dist_threshold_aft = pmax(0, pmin(data_check$dist_grade_cond, data_check$dist_ech_cond ))
data_check$dist_threshold= data_check$dist_threshold_bef + data_check$dist_threshold_aft


data_check$ind_exit      = ifelse(data_check$next_year!= "no_exit", 1, 0) 
data_check$ind_exit2      = ifelse(data_check$next_year == "exit_next", 1, 0) 

hz  = aggregate( ind_exit  ~ dist_threshold, data_check, mean )
hz2 = aggregate( ind_exit2 ~ dist_threshold, data_check, mean )
effectif = as.numeric(table(data_check$dist_threshold))

par(mar = c(5,5,2,5))
xlabel = ifelse(corps, "Duration in section", "Duration in rank")
plot(hz[,1], hz2[,2], type ="l", lwd = 3,  ylab = "Hazard rate", col = "darkcyan")
par(new = T)
plot(hz[,1], effectif, type ="l", lty = 2, lwd = 2, axes=F, xlab=NA, ylab=NA)
axis(side = 4)
mtext(side = 4, line = 3, 'Nb obs.')
legend("topleft", legend = c("Hazard", "Nb obs."), lwd = 3, lty = c(1,3), col = c("darkcyan", "black"), cex = 1.1)





#### Test thresholds TTH2 ####
data_stat_min =data_min[which(data_min$annee <= 2014 & data_min$annee >= 2011),]
data_check = data_stat_min[which(data_stat_min$c_cir_2011 == "TTH2" & data_stat_min$annee >= 2011),]
data_check = data_stat_max[which(data_stat_max$c_cir_2011 == "TTH2" & data_stat_max$annee >= 2011),]

#  Grade threshold
data_check$grade_cond = 6
data_check$time2 =  data_check$annee - data_check$an_aff +1 
data_check$dist_grade_cond = data_check$time2 - data_check$grade_cond

# Echelon threshold
cond_ech = 5
data_check$ech_cond = cond_ech

grille_ech = data.frame(echelon =  seq(1, 11), duree_min= c(12, 24, 24, 36, 36, 36, 48, 48, 48, 48, 48))
grille_ech$cum_duree = cumsum(grille_ech$duree_min)
ref = grille_ech$cum_duree[which(grille_ech$echelon ==cond_ech )]
grille_ech$dist_duree = grille_ech$cum_duree - ref

data_check = merge(data_check, grille_ech[, c(1,4)], by = "echelon", all.x = T) 
data_check$a = 1
data_check$duree_in_ech = ave(data_check$a, list(data_check$ident, data_check$grade, data_check$echelon), FUN = cumsum)
data_check$dist_ech_cond = (data_check$dist_duree)/12 + data_check$duree_in_ech


data_check$dist_threshold_bef = pmin(0, pmin(data_check$dist_grade_cond, data_check$dist_ech_cond ))
data_check$dist_threshold_aft = pmax(0, pmin(data_check$dist_grade_cond, data_check$dist_ech_cond ))
data_check$dist_threshold= data_check$dist_threshold_bef + data_check$dist_threshold_aft


data_check$ind_exit      = ifelse(data_check$next_year!= "no_exit", 1, 0) 
data_check$ind_exit2     = ifelse(data_check$next_year == "exit_next", 1, 0) 

aggregate( ind_exit2  ~ echelon, data_check, mean )
table(data_check$echelon)
aggregate( ind_exit2  ~ time2, data_check, mean )
table(data_check$time2)


hz  = aggregate( ind_exit  ~ dist_threshold, data_check, mean )
hz2 = aggregate( ind_exit2 ~ dist_threshold, data_check, mean )
effectif = as.numeric(table(data_check$dist_threshold))

corps = T
par(mar = c(5,5,2,5))
xlabel = ifelse(corps, "Duration in section", "Duration in rank")
plot(hz[,1], hz2[,2], type ="l", lwd = 3,  ylab = "Hazard rate", col = "darkcyan")
par(new = T)
plot(hz[,1], effectif, type ="l", lty = 2, lwd = 2, axes=F, xlab=NA, ylab=NA)
axis(side = 4)
mtext(side = 4, line = 3, 'Nb obs.')
legend("topleft", legend = c("Hazard", "Nb obs."), lwd = 3, lty = c(1,3), col = c("darkcyan", "black"), cex = 1.1)







#### Test thresholds TTH1 ####
data_check = data_stat_min[which(data_stat_min$c_cir_2011 == "TTH1" & data_stat_min$annee >= 2011),]
data_check = data_stat_max[which(data_stat_max$c_cir_2011 == "TTH1" & data_stat_max$annee >= 2011),]

#  Grade threshold
data_check$grade_cond = 10
data_check$time2 =  data_check$annee - data_check$an_aff +1 
data_check$dist_grade_cond = data_check$time2 - data_check$grade_cond

# Echelon threshold
cond_ech = 7
data_check$ech_cond = cond_ech

grille_ech = data.frame(echelon =  seq(1, 11), duree_min= c(12, 24, 24, 36, 36, 36, 48, 48, 48, 48, 48))
grille_ech$cum_duree = cumsum(grille_ech$duree_min)
ref = grille_ech$cum_duree[which(grille_ech$echelon ==cond_ech )]
grille_ech$dist_duree = grille_ech$cum_duree - ref

data_check = merge(data_check, grille_ech[, c(1,4)], by = "echelon", all.x = T) 
data_check$a = 1
data_check$duree_in_ech = ave(data_check$a, list(data_check$ident, data_check$grade, data_check$echelon), FUN = cumsum)
data_check$dist_ech_cond = (data_check$dist_duree)/12 + data_check$duree_in_ech


data_check$dist_threshold_bef = pmin(0, pmin(data_check$dist_grade_cond, data_check$dist_ech_cond ))
data_check$dist_threshold_aft = pmax(0, pmin(data_check$dist_grade_cond, data_check$dist_ech_cond ))
data_check$dist_threshold= data_check$dist_threshold_bef + data_check$dist_threshold_aft


data_check$ind_exit      = ifelse(data_check$next_year!= "no_exit", 1, 0) 
data_check$ind_exit2     = ifelse(data_check$next_year == "exit_next", 1, 0) 

aggregate( ind_exit2  ~ echelon, data_check, mean )
table(data_check$echelon)
aggregate( ind_exit2  ~ time2, data_check, mean )
table(data_check$time2)


hz  = aggregate( ind_exit  ~ dist_thresholdC, data_check, mean )
hz2 = aggregate( ind_exit2 ~ dist_thresholdC, data_check, mean )
effectif = as.numeric(table(data_check$dist_thresholdC))
x = which(effectif > 100)
corps = F
par(mar = c(5,5,2,5))
xlabel = ifelse(corps, "Duration in section", "Duration in rank")
plot(hz[x,1], hz2[x,2], type ="l", lwd = 3,  ylab = "Hazard rate", col = "darkcyan")
par(new = T)
plot(hz[x,1], effectif[x], type ="l", lty = 2, lwd = 2, axes=F, xlab=NA, ylab=NA)
axis(side = 4)
mtext(side = 4, line = 3, 'Nb obs.')
legend("topleft", legend = c("Hazard", "Nb obs."), lwd = 3, lty = c(1,3), col = c("darkcyan", "black"), cex = 1.1)



#### Check gains ib et echelon quand changement de grade

filename = paste0(data_path, "/filter/data_ATT_2011_filtered_after_duration_var_added_new.csv")
data_long = read.csv(filename)

y = 2014
g1 = "TTH3"
g2 = "TTH4"
list1 = data_long$ident[which(data_long$c_cir == g1 & data_long$grade_next == g2 & data_long$annee == y)]
data_check = data_long[which(is.element(data_long$ident, list1)),]
data_check = data_check[which(data_check$annee == y | data_check$annee == y+1), ]



echelon = data_check$echelon[which(data_check$annee == y)]
echelon_next = data_check$echelon[which(data_check$annee == y+1)]
table(echelon_next, echelon)
ib = data_check$ib[which(data_check$annee == y)]
ib_next = data_check$ib[which(data_check$annee == y+1)]

plot(echelon, echelon_next)
table(echelon_next, echelon)
plot(ib, ib_next)

#### Check evo ancienneté dans échelon prédite
load(paste0(simul_path, "predictions7_min.Rdata"))

colnames(output_global)
var = c('ident', 'annee', "grade_MNL_2",  'ib_MNL_2', 'echelon_MNL_2',  'anciennete_dans_echelon_MNL_2')
View(output_global[, var])






