library(OIsurv)
library(rms)
library(emuR)
library(RColorBrewer)
library(RcmdrPlugin.survival)
library(flexsurv)

data <- load_and_clean("M:/CNRACL/output/clean_data_finalisation/", "data_ATT_2002_2015_2.csv")

data_id <- data[[1]]
data_max <- data[[2]]
data_min <- data[[3]]

subdata <- data_id[which(data_id$left_censored == F),]

# Estimation de l'échelon passé
subdata_TTH3 <- subdata[which(subdata$c_cir_2011 == "TTH3"),]
subdata_TTH3$I_echelon <- as.numeric(subdata_TTH3$echelon == 6)

TTH3_long <- data_max[which(data_max$c_cir_2011 == 'TTH3'),]
TTH3_long <- TTH3_long[which(TTH3_long$left_censored == F),]
TTH3_long <- TTH3_long[which(TTH3_long$echelon == 6),]
time_min_in_ech_6 <- aggregate(TTH3_long$annee, by = list(TTH3_long$ident), min)
colnames(time_min_in_ech_6)[1] <- "ident"
colnames(time_min_in_ech_6)[2] <- "annee"
TTH3_long <- merge(TTH3_long, time_min_in_ech_6, by = c("ident", "annee"))
TTH3_long$duration_to_arrival_in_echelon_6 <- TTH3_long$annee - TTH3_long$annee_max_entree_dans_grade + 1

to_merge <- merge(subdata_TTH3, TTH3_long, by = "ident")
to_merge <- subset(to_merge, select=c("ident", "duration_to_arrival_in_echelon_6"))
subdata_TTH3 <- merge(subdata_TTH3, to_merge, by = "ident", all = TRUE)

subdata_TTH3 <- subset(
  subdata_TTH3,
  select = c('ident', 'sexe', 'generation_group', 'an_aff', 'duree_min', 'duration_to_arrival_in_echelon_6', 'right_censored')
  )

subdata_TTH3$right_censored = as.numeric(subdata_TTH3$right_censored)

new_subdata_TTH3 <- subdata_TTH3
attach(new_subdata_TTH3)

new_subdata_TTH3 <- tmerge(new_subdata_TTH3, subdata_TTH3, id = ident, tstop = duree_min)
new_subdata_TTH3 <- tmerge(new_subdata_TTH3, subdata_TTH3, id = ident, event_reach_ech_6 = event(duration_to_arrival_in_echelon_6))
new_subdata_TTH3$exit <- ifelse(new_subdata_TTH3$tstop == new_subdata_TTH3$duree_min & new_subdata_TTH3$right_censored != 1, 1, 0)

new_subdata_TTH3$passed_echelon_treshold <- ifelse(
  new_subdata_TTH3$tstart > 0, 1, 0)

new_subdata_TTH3 <- new_subdata_TTH3[which(new_subdata_TTH3$generation_group != 9),]

cox_time_varying <- coxph(
  formula = Surv(tstart, tstop, exit) ~ sexe + factor(generation_group) + passed_echelon_treshold + cluster(ident), data = new_subdata_TTH3
  )
summary(cox_time_varying)

# Checking the PH assumption
zp <- cox.zph(cox_time_varying, transform = function(time) log(time + 20))

# Estimation de l'impact de la durée passée dans le grade
subdata_TTH3 <- subdata[which(subdata$c_cir_2011 == "TTH3"),]
subdata_TTH3$duration_to_arrive_in_duration_5 <- ifelse(duree_min >= 5, 5, NA)
subdata_TTH3 <- subset(
  subdata_TTH3,
  select = c('ident', 'sexe', 'generation_group', 'an_aff', 'duree_min', 'duration_to_arrive_in_duration_5', 'right_censored')
  )
subdata_TTH3$right_censored = as.numeric(subdata_TTH3$right_censored)
new_subdata_TTH3 <- subdata_TTH3
attach(new_subdata_TTH3)
new_subdata_TTH3 <- tmerge(new_subdata_TTH3, subdata_TTH3, id = ident, tstop = duree_min)
new_subdata_TTH3 <- tmerge(new_subdata_TTH3, subdata_TTH3, id = ident, event_reach_duration_5 = event(duration_to_arrive_in_duration_5))
new_subdata_TTH3$exit <- ifelse(new_subdata_TTH3$tstop == new_subdata_TTH3$duree_min & new_subdata_TTH3$right_censored != 1, 1, 0)

new_subdata_TTH3$passed_grade_treshold <- ifelse(
  new_subdata_TTH3$tstart > 0, 1, 0
  )

cox_time_varying <- coxph(
  formula = Surv(tstart, tstop, exit) ~ sexe + factor(generation_group) + passed_grade_treshold + cluster(ident), data = new_subdata_TTH3
)
summary(cox_time_varying)