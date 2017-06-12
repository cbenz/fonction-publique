
##  Paths ####

rm(list = ls()); gc()
data_path = "M:/CNRACL/output/clean_data_finalisation/"
git_path =  'U:/Projets/CNRACL/fonction-publique/fonction_publique/'
wd =  'U:/Projets/CNRACL/fonction-publique/fonction_publique/estimation/'


fig_path = "Q:/CNRACL/Slides/Graphiques/"
tab_path = "Q:/CNRACL/Slides/Graphiques/"

#install.packages("OIsurv");install.packages("rms");install.packages("emuR");install.packages("RColorBrewer");install.packages("RcmdrPlugin");install.packages("flexsurv")
library(OIsurv)
library(rms)
library(emuR)
library(RColorBrewer)
library(RcmdrPlugin.survival)
library(flexsurv)