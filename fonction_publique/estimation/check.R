source(paste0(wd, "0_Outils_CNRACL.R"))
datasets = load_and_clean(data_path, "/filter/data_ATT_2011_filtered_after_duration_var_added_new.csv")
data_max = datasets[[1]]
data_min = datasets[[2]]

data_stat_min = data_min[which(data_min$left_censored == F & data_min$annee <= 2014),]
data_stat_max = data_max[which(data_max$left_censored == F & data_max$annee <= 2014),]



y = 2011
list1 = data_stat_min$ident[which(data_stat_min$grade == "TTH3" & data_stat_min$grade_next == "TTH4" & data_stat_min$annee == y)]
data_check = data_stat_min[which(is.element(data_stat_min$ident, list1)),]
data_check = data_check[which(data_check$annee == y | data_check$annee == y+1), ]
table(data_check$echelon[which(data_check$annee == y)])
table(data_check$time_spent_in_grade_min[which(data_check$annee == y)])
table(data_check$time_spent_in_grade_max[which(data_check$annee == y)])
