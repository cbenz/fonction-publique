################# Library of functions #######



## I. Packages

list_packages = list()
if (!require("pacman")) install.packages("pacman")
pacman::p_load(OIsurv, rms, emuR, RColorBrewer, flexsurv, mfx, 
               texreg, xtable, mlogit, data.table)


## I. Managing data #####

load_and_clean = function(data_path, dataname)
# Input: inital data (name and path)
# Ouput: two datasets, with two definitions of duration in grade
{
  ## Chargement de la base
  filename = paste0(data_path, dataname)
  data_long = read.csv(filename)

  ## Variables creation ####

  # Format bolean                     
  to_bolean = c("change_grade", "right_censored", "left_censored_min", "left_censored_max")
  data_long[, to_bolean] <- sapply(data_long[, to_bolean], as.logical)
  
  data_long$left_censored = data_long$left_censored_min  # pas de différenciation sur min/max car on filtre sur le plus exigeant
  data_long$observed  = ifelse(data_long$right_censored == 1, 0, 1) 
  data_long$echelon_2011 = ave(data_long$echelon*(data_long$annee == 2011), data_long$ident, FUN = max)
  data_long$last_y_in_grade = data_long$annee_exit - 1
  
  # Duration variables
  data_long$time_spent_in_grade_max  = data_long$annee - data_long$annee_entry_min + 1
  data_long$time_spent_in_grade_min  = data_long$annee - data_long$annee_entry_max + 1
  #data_long$time_spent_in_echelon    = 
    
  # Exit_status
  data_long$exit_status2 = ifelse(data_long$annee == data_long$last_y_in_grade, 1, 0)
  data_long$exit_status2[data_long$right_censored] = 0

  data_long$next_year = data_long$next_grade_situation

  data_long = data_long[order(data_long$ident,data_long$annee),]
  
  ## Institutional parameters (question: default value?)
  # Grade duration
  data_long$D_exam = 20
  data_long$D_exam[which(data_long$c_cir_2011 == "TTH1")] = 3
  data_long$D_choice = 20
  data_long$D_choice[which(data_long$c_cir_2011 == "TTH1")] = 10
  data_long$D_choice[which(data_long$c_cir_2011 == "TTH2")] = 6
  data_long$D_choice[which(data_long$c_cir_2011 == "TTH3")] = 5
  
  # Echelon (default = ?)
  data_long$E_exam = 12
  data_long$E_exam[which(data_long$c_cir_2011 == "TTH1")] = 4
  data_long$E_choice = 12
  data_long$E_choice[which(data_long$c_cir_2011 == "TTH1")] = 7
  data_long$E_choice[which(data_long$c_cir_2011 == "TTH2")] = 5
  data_long$E_choice[which(data_long$c_cir_2011 == "TTH3")] = 6
  
  # Next ib
  data_long$next_ib <-ave(data_long$ib, data_long$ident, FUN=shift1)
  data_long$var_ib  <-(data_long$next_ib - data_long$ib)/data_long$ib
  
  ## Data for estimations ####
  data_long = data_long[which(data_long$annee <= data_long$last_y_in_grade),]
  
  # One line per year of observation (min and max)
  data_min = data_long[which(data_long$annee >= data_long$annee_entry_min),]
  data_min$time = data_min$time_spent_in_grade_max 
  data_max = data_long[which(data_long$annee >= data_long$annee_entry_max),]
  data_max$time = data_max$time_spent_in_grade_min
  
  
  data_max = data_max[which(!is.element(data_max$ident, pb_ech)),]
  data_min = data_min[which(!is.element(data_min$ident, pb_ech)),]
  
  # One line per ident data
  data_id = data_long[!duplicated(data_long$ident),]
  
  return(list(data_max, data_min))
}  


# Variable creations 
create_variables <- function(data)
{
  data$dist_an_aff = data$annee - data$an_aff +1 
  grade_modif = which(data$c_cir_2011 == "TTH1" | data$c_cir_2011 == "TTH2")
  data$time2 = data$time
  data$time2[grade_modif] = data$dist_an_aff[grade_modif] 
  data$I_echC = ifelse(data$echelon >= data$E_choice, 1, 0) 
  data$I_gradeC   = ifelse(data$time2 >= data$D_choice, 1, 0) 
  data$I_gradeC   = ifelse(data$time2 >= data$D_choice, 1, 0) 
  data$I_bothC =  ifelse(data$I_echC ==1 &  data$I_gradeC == 1, 1, 0) 
  data$I_echE     = ifelse(data$echelon >= data$E_exam & data$c_cir_2011 == "TTH1", 1, 0) 
  data$I_gradeE   = ifelse(data$time2 >= data$D_exam & data$c_cir_2011 == "TTH1", 1, 0) 
  data$I_bothE    = ifelse(data$I_echE ==1 &  data$I_gradeE == 1, 1, 0) 
  data$c_cir = factor(data$c_cir)
  
  data$duration = data$time
  data$duration2 = data$time^2 
  
  data$duration  = data$time
  data$duration2 = data$time^2
  
  data$duration_aft  = data$time*data$I_bothC
  data$duration_aft2 = data$time^2*data$I_bothC
  
  data$duration_bef  = data$time*(1-data$I_bothC)
  data$duration_bef2 = data$time^2*(1-data$I_bothC)
  
  data$generation_group = factor(data$generation_group)
  data$c_cir_2011 = factor(data$c_cir_2011)
  
  # Unique threshold (first reached)
  grade_modif_bis = which(data$c_cir_2011 == "TTH1")
  data$I_unique_threshold = data$I_bothC
  data$I_unique_threshold[grade_modif_bis] = data$I_bothE[grade_modif_bis]
  
  data$duration_aft_unique_threshold  = data$time*data$I_unique_threshold
  data$duration_aft_unique_threshold2 = data$time^2*data$I_unique_threshold
  
  data$duration_bef_unique_threshold  = data$time*(1-data$I_unique_threshold)
  data$duration_bef_unique_threshold2 = data$time^2*(1-data$I_unique_threshold)
  
  
  return(data)
}


### II. Descriptive statistics

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


### III. Simulation tools ####
predict_next_year <- function(p1,p2,p3)
{
  # random draw of next year situation based on predicted probabilities   
  n = sample(c("no_exit", "exit_next",  "exit_oth"), size = 1, prob = c(p1,p2,p3), replace = T)  
  return(n) 
}  

predict_next_grade <- function(next_situation, grade, exit_oth)
  # Predict next grade based on next situation and current situation.
  {
  # Default: same grade
  next_grade = as.character(grade)
  # Exit next: next
  next_grade[which(grade == "TTH1" & next_situation == "exit_next")] = "TTH2"
  next_grade[which(grade == "TTH2" & next_situation == "exit_next")] = "TTH3"
  next_grade[which(grade == "TTH3" & next_situation == "exit_next")] = "TTH4"
  # Exit oth: draw in probability
  for (g in c("TTH1", "TTH2", "TTH3", "TTH4"))
  {
  list1 = which(grade == g & next_situation == "exit_oth")
  data1 = data_exit_oth[which(data_exit_oth$c_cir == g),]
  table1 = table(data1$next_grade)/length(data1$next_grade)
  next_grade[list1]  = sample(names(table1), size = length(list1), prob = as.vector(table1), replace = T)  
  }
  return(next_grade) 
}  


extract_exit = function(data, exit_var, name)
# Fonction computing for each individual in data the year of exit and the grade of destination.
{
  data = data[, c("ident", "annee", exit_var)]
  data$exit_var = data[, exit_var]
  data$ind_exit       = ifelse(data$exit_var != "no_exit", 1, 0) 
  data$ind_exit_cum   = ave(data$ind_exit, data$ident, FUN = cumsum)
  data$ind_exit_cum2  = ave(data$ind_exit_cum, data$ident, FUN = cumsum)
  data$ind_exit_cum2  = ave(data$ind_exit_cum, data$ident, FUN = cumsum)
  data$ind_exit_tot   = ave(data$ind_exit, data$ident, FUN = sum)
  data$ind_first_exit  = ifelse(data$ind_exit_cum2 == 1, 1, 0) 
  data$year_exit = ave((data$ind_first_exit*data$annee), data$ident, FUN = max)
  data$year_exit[which(data$year_exit == 0)] = 2014
  data2 = data[which(data$annee == data$year_exit ),]
  data2$year_exit[which(data2$ind_exit_tot == 0)] = 9999
  data2 = data2[c("ident", "year_exit", "exit_var")]
  colnames(data2)= paste0(colnames(data2), "_", name)
  return(data2)
}  


### IV. Generic functions 


shift<-function(x,shift_by){
  stopifnot(is.numeric(shift_by))
  stopifnot(is.numeric(x))
  
  if (length(shift_by)>1)
    return(sapply(shift_by,shift, x=x))
  
  out<-NULL
  abs_shift_by=abs(shift_by)
  if (shift_by > 0 )
    out<-c(tail(x,-abs_shift_by),rep(NA,abs_shift_by))
  else if (shift_by < 0 )
    out<-c(rep(NA,abs_shift_by), head(x,-abs_shift_by))
  else
    out<-x
  out
}


shiftm1<- function(x)  #adapt? de shift  : cr?er une variable d?cal?e de 1 vers le base. 
{
  out <- shift(x,-1)
  return(out)
}


shift1<-function(x){
  stopifnot(is.numeric(x))
  out<-NULL
  abs_shift_by=1
  out<-c(tail(x,-abs_shift_by),rep(NA,abs_shift_by))
  out
}

tirage<-function(var)
{
  t<-rbinom(1,1,var) # Loi binomiale 
  return(t)
}

build.ror <- function(final.rnames, name.map){
  keep <- final.rnames %in% names(name.map)
  mapper <- function(x){
    mp <- name.map[[x]] 
    ifelse(is.null(mp), x, mp)
  }
  newnames <- sapply(final.rnames, mapper)
  omit <- paste0(final.rnames[!keep], collapse="|")
  reorder <- na.omit(match(unlist(name.map), newnames[keep]))
  
  list(ccn=newnames, oc=omit, rc=reorder)
}

all.varnames.dammit <- function(model.list){
  mods <- texreg:::get.data(model.list)
  gofers <- texreg:::get.gof(mods)
  mm <- texreg:::aggregate.matrix(mods, gofers, digits=3)
  rownames(mm)
}


mfx <- function(x,sims=1000){
  set.seed(1984)
  pdf <- ifelse(as.character(x$call)[3]=="binomial(link = \"probit\")",
                mean(dnorm(predict(x, type = "link"))),
                mean(dlogis(predict(x, type = "link"))))
  pdfsd <- ifelse(as.character(x$call)[3]=="binomial(link = \"probit\")",
                  sd(dnorm(predict(x, type = "link"))),
                  sd(dlogis(predict(x, type = "link"))))
  marginal.effects <- pdf*coef(x)
  sim <- matrix(rep(NA,sims*length(coef(x))), nrow=sims)
  for(i in 1:length(coef(x))){
    sim[,i] <- rnorm(sims,coef(x)[i],diag(vcov(x)^0.5)[i])
  }
  pdfsim <- rnorm(sims,pdf,pdfsd)
  sim.se <- pdfsim*sim
  res <- cbind(marginal.effects,sd(sim.se))
  colnames(res)[2] <- "standard.error"
  ifelse(names(x$coefficients[1])=="(Intercept)",
         return(res[2:nrow(res),]),return(res))
}


mfx2<- function(modform,dist,data,boot=1000,digits=3){
  x <- glm(modform, family=binomial(link=dist),data)
  # get marginal effects
  pdf <- ifelse(dist=="probit",
                mean(dnorm(predict(x, type = "link"))),
                mean(dlogis(predict(x, type = "link"))))
  marginal.effects <- pdf*coef(x)
  # start bootstrap
  bootvals <- matrix(rep(NA,boot*length(coef(x))), nrow=boot)
  set.seed(1111)
  for(i in 1:boot){
    samp1 <- data[sample(1:dim(data)[1],replace=T,dim(data)[1]),]
    x1 <- glm(modform, family=binomial(link=dist),samp1)
    pdf1 <- ifelse(dist=="probit",
                   mean(dnorm(predict(x1, type = "link"))),
                   mean(dlogis(predict(x1, type = "link"))))
    bootvals[i,] <- pdf1*coef(x1)
  }
  res <- cbind(marginal.effects,apply(bootvals,2,sd),marginal.effects/apply(bootvals,2,sd))
  if(names(x$coefficients[1])=="(Intercept)"){
    res1 <- res[2:nrow(res),]
    res2 <- matrix(as.numeric(sprintf(paste("%.",paste(digits,"f",sep=""),sep=""),res1)),nrow=dim(res1)[1])     
    rownames(res2) <- rownames(res1)
  } else {
    res2 <- matrix(as.numeric(sprintf(paste("%.",paste(digits,"f",sep=""),sep="")),nrow=dim(res)[1]))
    rownames(res2) <- rownames(res)
  }
  colnames(res2) <- c("marginal.effect","standard.error","z.ratio")  
  return(res2)
}


extract.glm2 = function (model, include.aic = TRUE, include.bic = TRUE, include.loglik = TRUE, 
                         include.deviance = TRUE, include.nobs = TRUE, ...) 
{
  s <- summary(model, ...)
  coefficient.names <- rownames(s$coef)
  coefficients <- s$coef[, 1]
  standard.errors <- s$coef[, 2]
  significance <- s$coef[, 4]
  aic <- round(AIC(model))
  bic <- round(BIC(model))
  lik <- logLik(model)[1]
  dev <- deviance(model)
  n <- nobs(model)
  gof <- numeric()
  gof.names <- character()
  gof.decimal <- logical()
  if (include.aic == TRUE) {
    gof <- c(gof, aic)
    gof.names <- c(gof.names, "AIC")
    gof.decimal <- c(gof.decimal, TRUE)
  }
  if (include.bic == TRUE) {
    gof <- c(gof, bic)
    gof.names <- c(gof.names, "BIC")
    gof.decimal <- c(gof.decimal, TRUE)
  }
  if (include.loglik == TRUE) {
    gof <- c(gof, lik)
    gof.names <- c(gof.names, "Log Likelihood")
    gof.decimal <- c(gof.decimal, TRUE)
  }
  if (include.deviance == TRUE) {
    gof <- c(gof, dev)
    gof.names <- c(gof.names, "Deviance")
    gof.decimal <- c(gof.decimal, TRUE)
  }
  if (include.nobs == TRUE) {
    gof <- c(gof, n)
    gof.names <- c(gof.names, "Num. obs.")
    gof.decimal <- c(gof.decimal, FALSE)
  }
  tr <- createTexreg(coef.names = coefficient.names, coef = coefficients, 
                     se = standard.errors, pvalues = significance, gof.names = gof.names, 
                     gof = gof, gof.decimal = gof.decimal)
  return(tr)
}



