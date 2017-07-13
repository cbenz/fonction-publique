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

# Comparaison of IB distributions
summary(subset(data, select=c("ib_2012_obs", "ib_2012_m0", "ib_2012_m1", "ib_2012_m2")))

plot (density(data$ib_2012_obs), col = 'red')
lines (density(data$ib_2012_m0), col = 'green')
lines (density(data$ib_2012_m1), col = 'blue')
lines (density(data$ib_2012_m2), col = 'black')

data$grade_2011 <- factor(data$grade_2011, levels(data$grade_2012_obs))
data_ne_change_pas_grade <- data[which(data$grade_2011 == data$grade_2012_obs),]
summary(subset(data_ne_change_pas_grade, select=c("ib_2012_obs", "ib_2012_m0", "ib_2012_m1", "ib_2012_m2")))
plot (density(data_change_grade$ib_2012_obs), col = 'red')
lines (density(data_change_grade$ib_2012_m0), col = 'green')
lines (density(data_change_grade$ib_2012_m1), col = 'blue')
lines (density(data_change_grade$ib_2012_m2), col = 'black')

data_change_grade <- data[which(data$grade_2011 != data$grade_2012_obs),]
summary(subset(data_change_grade, select=c("ib_2012_obs", "ib_2012_m0", "ib_2012_m1", "ib_2012_m2")))
plot (density(data_change_grade$ib_2012_obs), col = 'red')
lines (density(data_change_grade$ib_2012_m0), col = 'green')
lines (density(data_change_grade$ib_2012_m1), col = 'blue')
lines (density(data_change_grade$ib_2012_m2), col = 'black')

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