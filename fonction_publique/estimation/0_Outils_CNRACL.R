################# Library of functions #######



## I. Packages
list_packages = list()
if (!require("pacman")) install.packages("pacman")
pacman::p_load(OIsurv, rms, emuR, RColorBrewer, flexsurv, mfx, devtools, plyr, 
               texreg, xtable, mlogit, data.table, pscl)


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
  
  data_long$grade = as.character(data_long$c_cir)
  
  # Duration variables
  data_long$time_spent_in_grade_max  = data_long$annee - data_long$annee_entry_min + 1
  data_long$time_spent_in_grade_min  = data_long$annee - data_long$annee_entry_max + 1
  data_long$anciennete_dans_echelon  = data_long$anciennete_echelon
  # Exit_status
  data_long$exit_status2 = ifelse(data_long$annee == data_long$last_y_in_grade, 1, 0)
  data_long$exit_status2[data_long$right_censored] = 0

  data_long$next_year = as.character(data_long$next_grade_situation)

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
  
  # One line per ident data
  data_id = data_long[!duplicated(data_long$ident),]
  
  # Tests
  stopifnot(length(unique(data_id$ident)) == length(unique(data_max$ident)) | length(unique(data_id$ident)) == length(unique(data_min$ident)))
  
  return(list(data_max, data_min))
}  


# Variable creations 
create_variables <- function(data)
{
  # Generation group
  data$generation_group  <-cut(data$generation, c(1960,1965,1970,1975,1980,1985,1990), labels=c(1:6))
  data$generation_group2 <-cut(data$generation, c(1960,1969,1979,1989), labels = c(1:3))
  
  data$age_an_aff    = data$an_aff - data$generation
  data$dist_an_aff = data$annee - data$an_aff +1 
  grade_modif = which(data$grade == "TTH1" | data$grade == "TTH2")
  data$time2 = data$time
  data$time2[grade_modif] = data$dist_an_aff[grade_modif] 
  data$I_echC     = ifelse(data$echelon >= data$E_choice, 1, 0) 
  data$I_gradeC   = ifelse(data$time2 >= data$D_choice, 1, 0) 
  data$I_gradeC   = ifelse(data$time2 >= data$D_choice, 1, 0) 
  data$I_bothC    =  ifelse(data$I_echC ==1 &  data$I_gradeC == 1, 1, 0) 
  data$I_echE     = ifelse(data$echelon >= data$E_exam & data$grade == "TTH1", 1, 0) 
  data$I_gradeE   = ifelse(data$time2 >= data$D_exam & data$grade == "TTH1", 1, 0) 
  data$I_bothE    = ifelse(data$I_echE ==1 &  data$I_gradeE == 1, 1, 0) 

  
  data$duration = data$time
  data$duration2 = data$time^2 
  data$duration3 = data$time^3 
  
  
  data$duration_aft  = data$time*data$I_bothC
  data$duration_aft2 = data$time^2*data$I_bothC
  
  data$duration_bef  = data$time*(1-data$I_bothC)
  data$duration_bef2 = data$time^2*(1-data$I_bothC)
  
  data$generation_group = factor(data$generation_group)
  data$c_cir_2011 = factor(data$c_cir_2011)
  
  # Unique threshold (first reached)
  grade_modif_bis = which(data$grade == "TTH1")
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
tirage_next_year_MNL <- function(p1,p2,p3)
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


build.ror <- function(final.rnames, name.map,add.omit=NULL){
  keep <- final.rnames %in% names(name.map)
  mapper <- function(x){
    mp <- name.map[[x]] 
    ifelse(is.null(mp), x, mp)
  }
  newnames <- sapply(final.rnames, mapper)
  omit <- paste0(paste0(final.rnames[!keep], collapse="|"),add.omit)
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


extract.glm2<-function (model, include.aic = F, include.bic = F, include.loglik = TRUE, 
                        include.deviance = F, include.nobs = TRUE,include.pseudoR2 = TRUE) 
{
  require(pscl)
  s <- summary(model)
  coefficient.names <- rownames(s$coef)
  coefficients <- s$coef[, 1]
  standard.errors <- s$coef[, 2]
  significance <- s$coef[, 4]
  lik <- logLik(model)[1]
  aic <- AIC(model)
  bic <- BIC(model)
  R2 <-pR2(model)[[4]]
  dev <- deviance(model)
  n <- nobs(model)
  gof <- numeric()
  gof.names <- character()
  gof.decimal <- logical()
  if (include.pseudoR2 == TRUE) {
    gof <- c(gof, R2)
    gof.names <- c(gof.names, "Pseudo R2")
    gof.decimal <- c(gof.decimal, TRUE)
  }
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



extract.mlogit2 <- function (model, include.aic = FALSE, include.loglik = TRUE, include.R2 = TRUE, include.nobs = TRUE)
{
  s <- summary(model)
  coefs <- s$CoefTable[, 1]
  rn <- rownames(s$CoefTable)
  se <- s$CoefTable[, 2]
  pval <- s$CoefTable[, 4]
  gof <- numeric()
  gof.names <- character()
  gof.decimal <- logical()
  if (include.R2 == TRUE) {
    gof <-  round(s$mfR2[1],3)
    gof.names <- c(gof.names, "Pseudo R2")
    gof.decimal <- c(gof.decimal, TRUE)
  }
  if (include.aic == TRUE) {
    gof <- AIC(model)
    gof.names <- c(gof.names, "AIC")
    gof.decimal <- c(gof.decimal, TRUE)
  }
  if (include.loglik == TRUE) {
    gof <- c(gof, logLik(model)[1])
    gof.names <- c(gof.names, "Log Likelihood")
    gof.decimal <- c(gof.decimal, TRUE)
  }
  if (include.nobs == TRUE) {
    gof <- c(gof, nrow(s$residuals))
    gof.names <- c(gof.names, "Num. obs.")
    gof.decimal <- c(gof.decimal, FALSE)
  }
  tr <- createTexreg(coef.names = rn, coef = coefs, se = se, 
                     pvalues = pval, gof.names = gof.names, gof = gof, gof.decimal = gof.decimal)
  return(tr)
}



texreg2 <- function (l, file = NULL, single.row = FALSE, stars = c(0.001,0.01, 0.05), custom.model.names = NULL, custom.coef.names = NULL, 
          custom.gof.names = NULL, custom.note = NULL, digits = 2, 
          leading.zero = TRUE, symbol = "\\cdot", override.coef = 0, 
          override.se = 0, override.pvalues = 0, override.ci.low = 0, 
          override.ci.up = 0, omit.coef = NULL, reorder.coef = NULL, 
          reorder.gof = NULL, ci.force = FALSE, ci.force.level = 0.95, 
          ci.test = 0, groups = NULL, custom.columns = NULL, custom.col.pos = NULL, 
          bold = 0, center = TRUE, caption = "Statistical models", 
          caption.above = FALSE, label = "table:coefficients", booktabs = FALSE, 
          dcolumn = FALSE, sideways = FALSE, longtable = FALSE, use.packages = TRUE, 
          table = TRUE, no.margin = FALSE, fontsize = NULL, scalebox = NULL, 
          float.pos = "", ...) {
  
  
  stars <- check.stars(stars)
  if (dcolumn == TRUE && bold > 0) {
    dcolumn <- FALSE
    msg <- paste("The dcolumn package and the bold argument cannot be used at", 
                 "the same time. Switching off dcolumn.")
    if (length(stars) > 1 || stars == TRUE) {
      warning(paste(msg, "You should also consider setting stars = 0."))
    }
    else {
      warning(msg)
    }
  }
  if (longtable == TRUE && sideways == TRUE) {
    sideways <- FALSE
    msg <- paste("The longtable package and sideways environment cannot be", 
                 "used at the same time. You may want to use the pdflscape package.", 
                 "Switching off sideways.")
    warning(msg)
  }
  if (longtable == TRUE && !(float.pos %in% c("", "l", "c", 
                                              "r"))) {
    float.pos <- ""
    msg <- paste("When the longtable environment is used, the float.pos", 
                 "argument can only take one of the \"l\", \"c\", \"r\", or \"\"", 
                 "(empty) values. Setting float.pos = \"\".")
    warning(msg)
  }
  if (longtable == TRUE && !is.null(scalebox)) {
    scalebox <- NULL
    warning(paste("longtable and scalebox are not compatible. Setting", 
                  "scalebox = NULL."))
  }
  models <- get.data(l, ...)
  gof.names <- get.gof(models)
  models <- override(models, override.coef, override.se, override.pvalues, 
                     override.ci.low, override.ci.up)
  models <- ciforce(models, ci.force = ci.force, ci.level = ci.force.level)
  models <- correctDuplicateCoefNames(models)
  gofs <- aggregate.matrix(models, gof.names, custom.gof.names, 
                           digits, returnobject = "gofs")
  m <- aggregate.matrix(models, gof.names, custom.gof.names, 
                        digits, returnobject = "m")
  decimal.matrix <- aggregate.matrix(models, gof.names, custom.gof.names, 
                                     digits, returnobject = "decimal.matrix")
  m <- customnames(m, custom.coef.names)
  m <- rearrangeMatrix(m)
  m <- as.data.frame(m)
  m <- omitcoef(m, omit.coef)
  m <- replaceSymbols(m)
  modnames <- modelnames(l, models, custom.model.names)
  m <- reorder(m, reorder.coef)
  gofs <- reorder(gofs, reorder.gof)
  decimal.matrix <- reorder(decimal.matrix, reorder.gof)
  lab.list <- c(rownames(m), gof.names)
  lab.length <- 0
  for (i in 1:length(lab.list)) {
    if (nchar(lab.list[i]) > lab.length) {
      lab.length <- nchar(lab.list[i])
    }
  }
  ci <- logical()
  for (i in 1:length(models)) {
    if (length(models[[i]]@se) == 0 && length(models[[i]]@ci.up) > 
        0) {
      ci[i] <- TRUE
    }
    else {
      ci[i] <- FALSE
    }
  }
  output.matrix <- outputmatrix(m, single.row, neginfstring = "\\multicolumn{1}{c}{$-\\infty$}", 
                                posinfstring = "\\multicolumn{1}{c}{$\\infty$}", leading.zero, 
                                digits, se.prefix = " \\; (", se.suffix = ")", star.prefix = "^{", 
                                star.suffix = "}", star.char = "*", stars, dcolumn = dcolumn, 
                                symbol, bold, bold.prefix = "\\mathbf{", bold.suffix = "}", 
                                ci = ci, semicolon = ";\\ ", ci.test = ci.test)
  output.matrix <- grouping(output.matrix, groups, indentation = "\\quad ", 
                            single.row = single.row, prefix = "", suffix = "")
  gof.matrix <- gofmatrix(gofs, decimal.matrix, dcolumn = TRUE, 
                          leading.zero, digits)
  output.matrix <- rbind(output.matrix, gof.matrix)
  output.matrix <- customcolumns(output.matrix, custom.columns, 
                                 custom.col.pos, single.row = single.row, numcoef = nrow(m), 
                                 groups = groups, modelnames = FALSE)
  coltypes <- customcolumnnames(modnames, custom.columns, custom.col.pos, 
                                types = TRUE)
  modnames <- customcolumnnames(modnames, custom.columns, custom.col.pos, 
                                types = FALSE)
  coldef <- ""
  if (no.margin == FALSE) {
    margin.arg <- ""
  }
  else {
    margin.arg <- "@{}"
  }
  coefcount <- 0
  for (i in 1:length(modnames)) {
    if (coltypes[i] == "coef") {
      coefcount <- coefcount + 1
    }
    if (single.row == TRUE && coltypes[i] == "coef") {
      if (ci[coefcount] == FALSE) {
        separator <- ")"
      }
      else {
        separator <- "]"
      }
    }
    else {
      separator <- "."
    }
    if (coltypes[i] %in% c("coef", "customcol")) {
      alignmentletter <- "c"
    }
    else if (coltypes[i] == "coefnames") {
      alignmentletter <- "l"
    }
    if (dcolumn == FALSE) {
      coldef <- paste0(coldef, alignmentletter, margin.arg, 
                       " ")
    }
    else {
      if (coltypes[i] != "coef") {
        coldef <- paste0(coldef, alignmentletter, margin.arg, 
                         " ")
      }
      else {
        if (single.row == TRUE) {
          dl <- compute.width(output.matrix[, i], left = TRUE, 
                              single.row = TRUE, bracket = separator)
          dr <- compute.width(output.matrix[, i], left = FALSE, 
                              single.row = TRUE, bracket = separator)
        }
        else {
          dl <- compute.width(output.matrix[, i], left = TRUE, 
                              single.row = FALSE, bracket = separator)
          dr <- compute.width(output.matrix[, i], left = FALSE, 
                              single.row = FALSE, bracket = separator)
        }
        coldef <- paste0(coldef, "D{", separator, "}{", 
                         separator, "}{", dl, separator, dr, "}", margin.arg, 
                         " ")
      }
    }
  }
  string <- "\n"
  if (use.packages == TRUE) {
    if (sideways == TRUE & table == TRUE) {
      string <- paste0(string, "\\usepackage{rotating}\n")
    }
    if (booktabs == TRUE) {
      string <- paste0(string, "\\usepackage{booktabs}\n")
    }
    if (dcolumn == TRUE) {
      string <- paste0(string, "\\usepackage{dcolumn}\n")
    }
    if (longtable == TRUE) {
      string <- paste0(string, "\\usepackage{longtable}\n")
    }
    if (dcolumn == TRUE || booktabs == TRUE || sideways == 
        TRUE || longtable == TRUE) {
      string <- paste0(string, "\n")
    }
  }
  if (longtable == TRUE) {
    if (center == TRUE) {
      string <- paste0(string, "\\begin{center}\n")
    }
    if (!is.null(fontsize)) {
      string <- paste0(string, "\\begin{", fontsize, "}\n")
    }
    if (float.pos == "") {
      string <- paste0(string, "\\begin{longtable}{", coldef, 
                       "}\n")
    }
    else {
      string <- paste0(string, "\\begin{longtable}[", float.pos, 
                       "]\n")
    }
  }
  else {
    if (table == TRUE) {
      if (sideways == TRUE) {
        t <- "sideways"
      }
      else {
        t <- ""
      }
      if (float.pos == "") {
        string <- paste0(string, "\\begin{", t, "table}\n")
      }
      else {
        string <- paste0(string, "\\begin{", t, "table}[", 
                         float.pos, "]\n")
      }
      if (caption.above == TRUE) {
        string <- paste0(string, "\\caption{", caption, 
                         "}\n")
      }
      if (center == TRUE) {
        string <- paste0(string, "\\begin{center}\n")
      }
      if (!is.null(fontsize)) {
        string <- paste0(string, "\\begin{", fontsize, 
                         "}\n")
      }
      if (!is.null(scalebox)) {
        string <- paste0(string, "\\scalebox{", scalebox, 
                         "}{\n")
      }
    }
    string <- paste0(string, "\\begin{tabular}{", coldef, 
                     "}\n")
  }
  tablehead <- ""
  if (booktabs == TRUE) {
    tablehead <- paste0(tablehead, "\\toprule\n")
  }
  else {
    tablehead <- paste0(tablehead, "\\hline\n")
  }
  tablehead <- paste0(tablehead, modnames[1])
  if (dcolumn == TRUE) {
    for (i in 2:length(modnames)) {
      if (coltypes[i] != "coef") {
        tablehead <- paste0(tablehead, " & ", modnames[i])
      }
      else {
        tablehead <- paste0(tablehead, " & \\multicolumn{1}{c}{", 
                            modnames[i], "}")
      }
    }
  }
  else {
    for (i in 2:length(modnames)) {
      tablehead <- paste0(tablehead, " & ", modnames[i])
    }
  }
  if (booktabs == TRUE) {
    tablehead <- paste0(tablehead, " \\\\\n", "\\midrule\n")
  }
  else {
    tablehead <- paste0(tablehead, " \\\\\n", "\\hline\n")
  }
  if (longtable == FALSE) {
    string <- paste0(string, tablehead)
  }
  if (is.null(stars)) {
    snote <- ""
  }
  else if (any(ci == FALSE)) {
    st <- sort(stars)
    if (length(unique(st)) != length(st)) {
      stop("Duplicate elements are not allowed in the stars argument.")
    }
    if (length(st) == 4) {
      snote <- paste0("$^{***}p<", st[1], "$, $^{**}p<", 
                      st[2], "$, $^*p<", st[3], "$, $^{", symbol, "}p<", 
                      st[4], "$")
    }
    else if (length(st) == 3) {
      snote <- paste0("$^{***}p<", st[1], "$, $^{**}p<", 
                      st[2], "$, $^*p<", st[3], "$")
    }
    else if (length(st) == 2) {
      snote <- paste0("$^{**}p<", st[1], "$, $^*p<", st[2], 
                      "$")
    }
    else if (length(st) == 1) {
      snote <- paste0("$^*p<", st[1], "$")
    }
    else {
      snote <- ""
    }
    if (is.numeric(ci.test) && !is.na(ci.test) && nchar(snote) > 
        0 && any(ci)) {
      snote <- paste(snote, "(or", ci.test, "outside the confidence interval).")
    }
    else if (is.numeric(ci.test) && !is.na(ci.test) && any(ci)) {
      snote <- paste("$^*$", ci.test, "outside the confidence interval")
    }
  }
  else if (is.numeric(ci.test) && !is.na(ci.test)) {
    snote <- paste("$^*$", ci.test, "outside the confidence interval")
  }
  else {
    snote <- ""
  }
  if (is.null(fontsize)) {
    notesize <- "scriptsize"
  }
  else if (fontsize == "tiny" || fontsize == "scriptsize" || 
           fontsize == "footnotesize" || fontsize == "small") {
    notesize <- "tiny"
  }
  else if (fontsize == "normalsize") {
    notesize <- "scriptsize"
  }
  else if (fontsize == "large") {
    notesize <- "footnotesize"
  }
  else if (fontsize == "Large") {
    notesize <- "small"
  }
  else if (fontsize == "LARGE") {
    notesize <- "normalsize"
  }
  else if (fontsize == "huge") {
    notesize <- "large"
  }
  else if (fontsize == "Huge") {
    notesize <- "Large"
  }
  if (is.null(custom.note)) {
    note <- paste0("\\multicolumn{", length(modnames), "}{l}{\\", 
                   notesize, "{", snote, "}}")
  }
  else if (custom.note == "") {
    note <- ""
  }
  else {
    note <- paste0("\\multicolumn{", length(modnames), "}{l}{\\", 
                   notesize, "{", custom.note, "}}")
    note <- gsub("%stars", snote, note, perl = TRUE)
  }
  if (longtable == TRUE) {
    note <- paste0(note, "\\\\\n")
  }
  else {
    note <- paste0(note, "\n")
  }
  if (booktabs == TRUE) {
    bottomline <- "\\bottomrule\n"
  }
  else {
    bottomline <- "\\hline\n"
  }
  if (longtable == TRUE) {
    if (caption.above == TRUE) {
      string <- paste0(string, "\\caption{", caption, "}\n", 
                       "\\label{", label, "}\\\\\n", tablehead, "\\endfirsthead\n", 
                       tablehead, "\\endhead\n", bottomline, "\\endfoot\n", 
                       bottomline, note, "\\endlastfoot\n")
    }
    else {
      string <- paste0(string, tablehead, "\\endfirsthead\n", 
                       tablehead, "\\endhead\n", bottomline, "\\endfoot\n", 
                       bottomline, note, "\\caption{", caption, "}\n", 
                       "\\label{", label, "}\n", "\\endlastfoot\n")
    }
  }
  max.lengths <- numeric(length(output.matrix[1, ]))
  for (i in 1:length(output.matrix[1, ])) {
    max.length <- 0
    for (j in 1:length(output.matrix[, 1])) {
      if (nchar(output.matrix[j, i]) > max.length) {
        max.length <- nchar(output.matrix[j, i])
      }
    }
    max.lengths[i] <- max.length
  }
  for (i in 1:length(output.matrix[, 1])) {
    for (j in 1:length(output.matrix[1, ])) {
      nzero <- max.lengths[j] - nchar(output.matrix[i, 
                                                    j])
      zeros <- rep(" ", nzero)
      zeros <- paste(zeros, collapse = "")
      output.matrix[i, j] <- paste0(output.matrix[i, j], 
                                    zeros)
    }
  }
  for (i in 1:(length(output.matrix[, 1]) - length(gof.names))) {
    for (j in 1:length(output.matrix[1, ])) {
      string <- paste0(string, output.matrix[i, j])
      if (j == length(output.matrix[1, ])) {
        string <- paste0(string, " \\\\\n")
      }
      else {
        string <- paste0(string, " & ")
      }
    }
  }
  if (length(gof.names) > 0) {
    if (booktabs == TRUE) {
      string <- paste0(string, "\\midrule\n")
    }
    else {
      string <- paste0(string, "\\hline\n")
    }
    for (i in (length(output.matrix[, 1]) - (length(gof.names) - 
                                             1)):(length(output.matrix[, 1]))) {
      for (j in 1:length(output.matrix[1, ])) {
        string <- paste0(string, output.matrix[i, j])
        if (j == length(output.matrix[1, ])) {
          string <- paste0(string, " \\\\\n")
        }
        else {
          string <- paste0(string, " & ")
        }
      }
    }
  }
  if (longtable == FALSE) {
    string <- paste0(string, bottomline)
    string <- paste0(string, note, "\\end{tabular}\n")
  }
  if (longtable == TRUE) {
    string <- paste0(string, "\\end{longtable}\n")
    if (!is.null(fontsize)) {
      string <- paste0(string, "\\end{", fontsize, "}\n")
    }
    if (center == TRUE) {
      string <- paste0(string, "\\end{center}\n")
    }
  }
  else if (table == TRUE) {
    if (!is.null(fontsize)) {
      string <- paste0(string, "\\end{", fontsize, "}\n")
    }
    if (!is.null(scalebox)) {
      string <- paste0(string, "}\n")
    }
    if (caption.above == FALSE) {
      string <- paste0(string, "\\caption{", caption, "}\n")
    }
    string <- paste0(string, "\\label{", label, "}\n")
    if (center == TRUE) {
      string <- paste0(string, "\\end{center}\n")
    }
    if (sideways == TRUE) {
      t <- "sideways"
    }
    else {
      t <- ""
    }
    string <- paste0(string, "\\end{", t, "table}\n")
  }
  if (is.null(file) || is.na(file)) {
    class(string) <- c("character", "texregTable")
    return(string)
  }
  else if (!is.character(file)) {
    stop("The 'file' argument must be a character string.")
  }
  else {
    sink(file)
    cat(string)
    sink()
    message(paste0("The table was written to the file '", 
                   file, "'.\n"))
  }
}
environment(texreg2) = environment(texreg)