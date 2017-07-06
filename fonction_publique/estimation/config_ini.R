
##  Paths ####
rm(list = ls()); gc()

place = "IPP_S"
#place = "home_S"

if (place == "home_S")
{  
data_path = "/Users/simonrabate/Desktop/data/CNRACL/output/"
git_path =  '/Users/simonrabate/Desktop/IPP/CNRACL'
wd =  '/Users/simonrabate/Desktop/IPP/CNRACL/fonction_publique/estimation/'
fig_path = "Q:/CNRACL/Slides/2017_06_IMA/Graphiques/"
tab_path = "Q:/CNRACL/Slides/2017_06_IMA/Graphiques/"
}

if (place == "IPP_S")
{  
data_path = "M:/CNRACL/output/clean_data_finalisation/"
git_path =  'U:/Projets/CNRACL/fonction-publique/fonction_publique/'
wd =  'U:/Projets/CNRACL/fonction-publique/fonction_publique/estimation/'
fig_path = "Q:/CNRACL/Slides/2017_06_IMA/Graphiques/"
tab_path = "Q:/CNRACL/Slides/2017_06_IMA/Graphiques/"
}




#install.packages("OIsurv");install.packages("rms");install.packages("emuR");install.packages("RColorBrewer");
# install.packages("RcmdrPlugin");install.packages("flexsurv"); install.packages("mfx") ; install.packages("texreg")
# ; install.packages("mlogit")
library(OIsurv)
library(rms)
library(emuR)
library(RColorBrewer)
library(RcmdrPlugin.survival)
library(flexsurv)

library(mfx)
library(texreg)
library(xtable)




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

