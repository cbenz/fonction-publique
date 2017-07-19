# Paths
asset_simulation_path <- 'M:/CNRACL/simulation/'
data_path <- 'M:/CNRACL/output/clean_data_finalisation/'

# Load data and reshape data
input <- read.csv(paste0(asset_simulation_path, 'data_simul_2011_m0.csv'))
input <- subset(input, select=c("ident", "grade", "echelon", "ib"))
colnames(input) <- c('ident', 'grade_2011', 'echelon_2011', 'ib_2011')



results_raw <- list(read.csv(paste0(asset_simulation_path, 'results_2011_m0.csv')),
            read.csv(paste0(asset_simulation_path, 'results_2011_m1.csv')),
            read.csv(paste0(asset_simulation_path, 'results_2011_m2.csv'))
            )
results_list <- c()
it <- 1
model_names <- c("_m0", "_m1", "_m2")
for (i in model_names)
  {

  data <- read.csv(paste0(asset_simulation_path, 'results_2011', i, '.csv'))
  data <- subset(data, select=c("ident", "grade", "echelon", "ib"))
  colnames(data) <- c('ident', paste0('grade_2012', i), paste0('echelon_2012', i), paste0('ib_2012', i))
  results_list[[it]] <- data
  it <- it+1
}
results <- merge(results_list[[1]], results_list[[2]], by = 'ident')
results <- merge(results, results_list[[3]], by = 'ident')

observed <- read.csv(paste0(data_path, 'data_ATT_2002_2015_with_filter_on_etat_at_exit_and_change_to_filter_on_etat_grade_corrected.csv'))
observed <- subset(observed, annee == 2012, select=c("ident", "c_cir", "echelon", "ib"))
colnames(observed) <- c('ident', 'grade_2012_obs', 'echelon_2012_obs', 'ib_2012_obs')

data <- merge(input, results, by = 'ident')
data <- merge(data, observed, by = 'ident')

data$difference_m0 <- abs(data$ib_2012_obs - data$ib_2012_m0)
data$difference_m1 <- abs(data$ib_2012_obs - data$ib_2012_m1) 
data$difference_m2 <- abs(data$ib_2012_obs - data$ib_2012_m2)

data$var_ib_obs = data$ib_2012_obs - data$ib_2011
data$var_ib_m0 = data$ib_2012_m0 - data$ib_2011
data$var_ib_m1 = data$ib_2012_m1 - data$ib_2011
data$var_ib_m2 = data$ib_2012_m2 - data$ib_2011

data$var_ech_obs = data$echelon_2012_obs - data$echelon_2011
data$var_ech_m0  = data$echelon_2012_m0 - data$echelon_2011
data$var_ech_m1  = data$echelon_2012_m1 - data$echelon_2011
data$var_ech_m2  = data$echelon_2012_m2 - data$echelon_2011


data$grade_2011 = as.character(data$grade_2011)
data$grade_2012_m0 =  as.character(data$grade_2012_m0)
data$grade_2012_m1 =  as.character(data$grade_2012_m1)
data$grade_2012_m2 =  as.character(data$grade_2012_m2)
data$grade_2012_obs =  as.character(data$grade_2012_obs)




# Filters for 
data = data[which(data$ib_2011<=450), ]

### CHECKS

l1 = which(as.character(data$grade_2011) != as.character(data$grade_2012_m1))
l2 = which(as.character(data$grade_2011) == as.character(data$grade_2012_m1))
table(data$ib_2012_obs[l1] - data$ib_2011[l1])
table(data$ib_2012_m1[l1] - data$ib_2011[l1])
table(data$ib_2012_obs[l2] - data$ib_2011[l2])
table(data$ib_2012_m1[l2] - data$ib_2011[l2])

## Masse des ib
sum(data$ib_2012_obs)
(sum(data$ib_2012_m0) - sum(data$ib_2012_obs))/sum(data$ib_2012_obs)
(sum(data$ib_2012_m1) - sum(data$ib_2012_obs))/sum(data$ib_2012_obs)
(sum(data$ib_2012_m2) - sum(data$ib_2012_obs))/sum(data$ib_2012_obs)

a <- sum(data$ib_2012_obs[which(data$grade_2011 != data$grade_2012_obs)])
b <- sum(data$ib_2012_m0[which(data$grade_2011 != data$grade_2012_m0)])
c <- sum(data$ib_2012_m1[which(data$grade_2011 != data$grade_2012_m1)])
d <- sum(data$ib_2012_m2[which(data$grade_2011 != data$grade_2012_m2)])
(b-a)/a
(c-a)/a
(d-a)/a

a <- sum(data$ib_2012_obs[which(data$grade_2011 == data$grade_2012_obs)])
b <- sum(data$ib_2012_m0[which(data$grade_2011 == data$grade_2012_m0)])
c <- sum(data$ib_2012_m1[which(data$grade_2011 == data$grade_2012_m1)])
d <- sum(data$ib_2012_m2[which(data$grade_2011 == data$grade_2012_m2)])
(b-a)/a
(c-a)/a
(d-a)/a



#### Comparison of IB distributions
summary(subset(data, select=c("ib_2012_obs", "ib_2012_m0", "ib_2012_m1", "ib_2012_m2")))
plot (density(data$ib_2012_obs), col = 'red', ylim = c(0, 0.04), xlim = c(275, 450))
lines (density(data$ib_2012_m0), col = 'green')
lines (density(data$ib_2012_m1), col = 'blue')
lines (density(data$ib_2012_m2), col = 'black')


plot  (density(data$ib_2012_obs[which(data$grade_2011 == data$grade_2012_obs)]), col = 'red', xlim = c(275, 450))
lines (density(data$ib_2012_m0[which(data$grade_2011 == data$grade_2012_m0)]), col = 'green')
lines (density(data$ib_2012_m1[which(data$grade_2011 == data$grade_2012_m1)]), col = 'blue')
lines (density(data$ib_2012_m2[which(data$grade_2011 == data$grade_2012_m2)]), col = 'black')

plot  (density(data$ib_2012_obs[which(data$grade_2011 != data$grade_2012_obs)]), col = 'red', ylim = c(0, 0.025), xlim = c(275, 450),
       main = "")
lines (density(data$ib_2012_m0[which(data$grade_2011 != data$grade_2012_m0)]), col = 'green')
lines (density(data$ib_2012_m1[which(data$grade_2011 != data$grade_2012_m1)]), col = 'blue')
lines (density(data$ib_2012_m2[which(data$grade_2011 != data$grade_2012_m2)]), col = 'black')
legend("topright", legend = c("Obs", "m0", "m1", "m2"), col = c('red', 'green', 'blue','black'), lty =1, lwd = 3)

set.seed(123)
brks <- with(data, quantile(ib_2011, probs = c(0, 0.25, 0.5, 0.75, 1)))
data <- within(data, quartile_ib_2011 <- cut(ib_2011, breaks = brks, labels = 1:4, 
                                     include.lowest = TRUE))
for (i in 4)
  {
  data_quartile <- data[which(data$quartile_ib_2011 == i),]
  print(summary(subset(data_quartile, select=c("ib_2012_obs", "ib_2012_m0", "ib_2012_m1", "ib_2012_m2"))))
  plot (density(data_quartile$ib_2012_obs), col = 'red')
  lines (density(data_quartile$ib_2012_m0), col = 'green')
  lines (density(data_quartile$ib_2012_m1), col = 'blue')
  lines (density(data_quartile$ib_2012_m2), col = 'black')
  }

grades <- c('TTH1', 'TTH2', 'TTH3', 'TTH4')
for (i in 1:4)
  {
  data_grade <- data[which(data$grade_2011 == grades[i]),]
  print(summary(subset(data_grade, select=c("ib_2012_obs", "ib_2012_m0", "ib_2012_m1", "ib_2012_m2"))))
  }

# Comparison of distributions of IB differences
summary(subset(data, select=c('difference_m0', 'difference_m1', 'difference_m2')))




# 
summary(subset(data, select=c("var_ib_obs", "var_ib_m0", "var_ib_m1", "var_ib_m2")))
summary(data$var_ib_obs[which(data$grade_2011 != data$grade_2012_obs)])
summary(data$var_ib_m0[which(data$grade_2011 != data$grade_2012_m0)])
summary(data$var_ib_m1[which(data$grade_2011 != data$grade_2012_m1)])
summary(data$var_ib_m2[which(data$grade_2011 != data$grade_2012_m2)])

summary(data$var_ib_obs[which(data$grade_2011 != data$grade_2012_obs & data$grade_2011 == "TTH1")])
summary(data$var_ib_m0[which(data$grade_2011 != data$grade_2012_m0   & data$grade_2011 == "TTH1")])
summary(data$var_ib_m1[which(data$grade_2011 != data$grade_2012_m1   & data$grade_2011 == "TTH1")])
summary(data$var_ib_m2[which(data$grade_2011 != data$grade_2012_m2   & data$grade_2011 == "TTH1")])

summary(data$var_ib_obs[which(data$grade_2011 != data$grade_2012_obs & data$grade_2011 == "TTH2")])
summary(data$var_ib_m0[which(data$grade_2011 != data$grade_2012_m0   & data$grade_2011 == "TTH2")])
summary(data$var_ib_m1[which(data$grade_2011 != data$grade_2012_m1   & data$grade_2011 == "TTH2")])
summary(data$var_ib_m2[which(data$grade_2011 != data$grade_2012_m2   & data$grade_2011 == "TTH2")])

summary(data$var_ib_obs[which(data$grade_2011 != data$grade_2012_obs & data$grade_2011 == "TTH3")])
summary(data$var_ib_m0[which(data$grade_2011 != data$grade_2012_m0   & data$grade_2011 == "TTH3")])
summary(data$var_ib_m1[which(data$grade_2011 != data$grade_2012_m1   & data$grade_2011 == "TTH3")])
summary(data$var_ib_m2[which(data$grade_2011 != data$grade_2012_m2   & data$grade_2011 == "TTH3")])

summary(data$var_ib_obs[which(data$grade_2011 != data$grade_2012_obs & data$grade_2011 == "TTH4")])
summary(data$var_ib_m0[which(data$grade_2011 != data$grade_2012_m0   & data$grade_2011 == "TTH4")])
summary(data$var_ib_m1[which(data$grade_2011 != data$grade_2012_m1   & data$grade_2011 == "TTH4")])
summary(data$var_ib_m2[which(data$grade_2011 != data$grade_2012_m2   & data$grade_2011 == "TTH4")])


## Différence d'ib quand bon match
list_m0 = which(data$grade_2011 != data$grade_2012_obs &  data$grade_2012_obs ==  data$grade_2012_m0)
list_m1 = which(data$grade_2011 != data$grade_2012_obs &  data$grade_2012_obs ==  data$grade_2012_m1)
list_m2 = which(data$grade_2011 != data$grade_2012_obs &  data$grade_2012_obs ==  data$grade_2012_m2)

summary(data$var_ib_obs[list_m0])
summary(data$var_ib_m0[list_m0])
summary(data$var_ib_obs[list_m1])
summary(data$var_ib_m1[list_m1])
summary(data$var_ib_obs[list_m2])
summary(data$var_ib_m2[list_m2])




# Diff ech
table(data$var_ech_obs[which(data$grade_2011 == data$grade_2012_obs)])/length(which(data$grade_2011 == data$grade_2012_obs))
table(data$var_ech_m2[which(data$grade_2011 == data$grade_2012_m2)])/length(which(data$grade_2011 == data$grade_2012_m2))



