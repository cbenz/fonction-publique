######################################################################################################################## 
######################################## TRAJECTORIES in ADJOINT TECHNIQUE CORPS ######################################
######################################################################################################################## 


#### 0. Initialisation ####

rm(list = ls()); gc()

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
 
filename = paste0(data_path,"bases_AT_imputations_trajectoires_avant_2011/corpsAT_2007.csv")
main = read.csv(filename)  


table(main$etat4)

### I. Check missing ib/etat ####

# Reshape echelon et etat
data = main[which(main$annee >= 2011),c("ident", "annee", "echelon1", "echelon2", "echelon3", "echelon4")]
data_ech = reshape(data, idvar = c("ident", "annee"), v.names = "ech", timevar = "trimestre",
               varying = c("echelon1", "echelon2", "echelon3", "echelon4") , direction = "long")
data = main[which(main$annee >= 2011),c("ident", "annee","etat1", "etat2", "etat3", "etat4")]
data_etat = reshape(data, idvar = c("ident", "annee"), v.names = "etat", timevar = "trimestre",
                   varying = c("etat1", "etat2", "etat3", "etat4") , direction = "long")
data = main[which(main$annee >= 2011),c("ident", "annee","ib1", "ib2", "ib3", "ib4")]
data_ib = reshape(data, idvar = c("ident", "annee"), v.names = "ib", timevar = "trimestre",
                    varying = c("ib1", "ib2", "ib3", "ib4") , direction = "long")


# Reshape echelon et etat
data = main[which(main$annee <= 2011),c("ident", "annee", "echelon1", "echelon2", "echelon3", "echelon4")]
data_ech = reshape(data, idvar = c("ident", "annee"), v.names = "ech", timevar = "trimestre",
                   varying = c("echelon1", "echelon2", "echelon3", "echelon4") , direction = "long")
data = main[which(main$annee <= 2011),c("ident", "annee","etat1", "etat2", "etat3", "etat4")]
data_etat = reshape(data, idvar = c("ident", "annee"), v.names = "etat", timevar = "trimestre",
                    varying = c("etat1", "etat2", "etat3", "etat4") , direction = "long")
data = main[which(main$annee <= 2011),c("ident", "annee","ib1", "ib2", "ib3", "ib4")]
data_ib = reshape(data, idvar = c("ident", "annee"), v.names = "ib", timevar = "trimestre",
                  varying = c("ib1", "ib2", "ib3", "ib4") , direction = "long")

ib =  data_ib$ib
etat = data_etat$etat
data_long = cbind(data_ech, ib,etat)
data_long$ib2 = data_long$ib
data_long$ib2[ib > 0] = 1

attach(data_long)
length(which(ib == 0))
length(which(ib == -1)) 
length(which(is.na(ib)))

table(etat[which(ib == 0)])
table(etat[which(ib == -1)] )
table(etat[which(ib == -1)])/length(etat[which(ib ==-1)])


table(etat[which(ib == -1 & annee == 2011)])
table(etat[which(ib == -1 & annee == 2008)])

table(etat[which(ib == -1 & annee == 2011)])/length(etat[which(ib ==-1 & annee == 2011)])

table(etat[which(ib > 0)])/length(etat[which(ib > 0)])
table(ib2[etat>0])

detach(data_long)

sort(table(ib),decreasing=TRUE)[1:10]



### II. Check an affiliation pour entrée en THH1 ####

data = main[which(main$annee >= 2011 & main$generation > 1960), c("ident", "generation", "annee", "c_cir", "an_aff",  "etat4")]
data$c_cir[which(data$c_cir == "STH1")] = "TTH1" 
data$c_cir[which(data$c_cir == "TTA1")] = "TTH1" 
data$c_cir[which(data$c_cir == "BTH1")] = "TTH1" 


## Filtres: 
# CIR manquant et état==1
list_ident1 =  data$ident[which(data$c_cir == "" & data$etat4>0)]

data = data[-which(is.element(data$ident, list_ident1)),]

year = 2013
year_bef = year -1

list_tth1 = data$ident[which(data$c_cir == "TTH1" & data$annee == year)]
list_no_tth1_bef = data$ident[which(data$c_cir != "TTH1" & data$annee == year_bef)]
list_entry_tth1 = intersect(list_tth1, list_no_tth1_bef)

sub_data = data[which(is.element(data$ident, list_entry_tth1) & data$annee == year_bef), ]

nrow(sub_data)
sort(table(sub_data$c_cir), decreasing = T)
table(sub_data$an_aff)

length(which(sub_data$c_cir == ""))/nrow(sub_data)
length(which(sub_data$an_aff >= year_bef))/nrow(sub_data)

View(main[which(is.element(main$ident,sub_data$ident[which(sub_data$an_aff == 2007)])),])


