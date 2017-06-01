
#### Censoring analysis ####


# path
place = "ippS"
if (place == "ippS"){
  data_path = "M:/CNRACL/output/"
  git_path =  'U:/Projets/CNRACL/fonction-publique/fonction_publique/'
}
if (place == "ippL"){
  data_path = "M:/CNRACL/output/"
  git_path =  'C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/'
}
if (place == "mac"){
  data_path = "/Users/simonrabate/Desktop/data/CNRACL/"
  git_path =  '/Users/simonrabate/Desktop/IPP/CNRACL/fonction_publique/'
}
fig_path = paste0(git_path,"ecrits/modelisation_carriere/Figures/")
tab_path = paste0(git_path,"ecrits/modelisation_carriere/Tables/")

### Loading packages and functions ###
source(paste0(git_path, 'modelisation/OutilsCNRACL.R'))


# Read csv
filename = paste0(data_path,"base_AT_clean_2007_2011/data_non_chgmt.csv")
left_censored = read.csv(filename)  
filename = paste0(data_path,"base_AT_clean_2007_2011/data_chgmt.csv")
not_censored = read.csv(filename)  

### I. Work on data ####

# Not censored
not_censored$ind_left_censoring = 0
not_censored$cir_2011 = not_censored$c_cir_2011
for (a in 2010:2008)
{  
var = paste0("c_cir_",a)
not_censored$cir_2011[which(not_censored$cir_2011 == "") ] = not_censored[which(not_censored$cir_2011 == ""), var]
}


# Censored
left_censored$ind_left_censoring = 1
left_censored$cir_2011 = left_censored$c_cir_2008
left_censored = left_censored[!duplicated(left_censored$ident),]

# Remove individuals in both dataset 
list_common = intersect(not_censored$ident, left_censored$ident)
not_censored = not_censored[-which(is.element(not_censored$ident, list_common)),]



# Common dataset
data = rbind(not_censored[, c("ident", "cir_2011", "ind_left_censoring")], left_censored[, c("ident", "cir_2011", "ind_left_censoring")])


### II. Sample description ####

attach(data)

table(cir_2011)
table(cir_2011[ind_left_censoring == 1])
table(cir_2011[ind_left_censoring == 0])


stat = matrix(ncol = 5, nrow = 10)

# Nb observation






detach(data)




