######################################################################################################################## 
######################################## TRAJECTORIES in ADJOINT TECHNIQUE CORPS ######################################
######################################################################################################################## 


#### 0. Initialisation ####


# path
place = "ipp"
if (place == "ipp"){
data_path = "M:/CNRACL/output/"
git_path =  'U:/Projets/CNRACL/fonction-publique/fonction_publique/'
}
if (place == "mac"){
  data_path = "/Users/simonrabate/Desktop/data/CNRACL/"
  git_path =  '/Users/simonrabate/Desktop/IPP/CNRACL/fonction_publique/'
}
fig_path = paste0(git_path,"ecrits/modelisation_carriere/Figures/")


                  
  
  ### Loading packages and functions ###
source(paste0(git_path, 'modelisation/OutilsCNRACL.R'))


                  

# Read csv
main = read.csv(paste0(data_path,"corpsAT.csv"))

ident = unique(main$ident)
sub = sample(ident, 10000)
sub_data = main[which(is.element(main$ident, sub)), ]

data = sub_data
data = main

#### I. WOD ####
data$libemploi = as.character(data$libemploi)
data$c_neg = as.numeric(format(data$c_neg))
data$c_neg[which(is.na(data$c_neg))] <- 0

# List of AT neg
list_neg = c(793, 794, 795, 796)
# First/last
data$a     <- 1
data$b     <- ave(data$a,data$ident,FUN=cumsum)
data$c     <- ave(data$a,data$ident,FUN=sum)
data$first <- ifelse(data$b==1,1,0)
data$last  <- ifelse(data$b==data$c,1,0)
data$count = data$b
data <- data[, !names(data) %in% c('a', 'b', 'c')]
# AT variables
data$ind_AT = ifelse(is.element(data$c_neg, list_neg), 1, 0) 

data$a = ave(data$ind_AT,data$ident,FUN=cumsum)
data$first_AT <- ifelse(data$a==1,1,0)
data$count_AT <-  ave(data$ind_AT, data$ident, FUN = sum)


## Correction: si grade[n-1] = grade[n+1] et != grade[n] on modifie grade[n]
data$bef_neg  <-ave(data$c_neg, data$ident, FUN=shiftm1)
data = slide(data, "libemploi", GroupVar = "ident", NewVar = "bef_lib", slideBy = -1,
             keepInvalid = FALSE, reminder = TRUE)
data$next_neg <-ave(data$c_neg, data$ident, FUN=shift1)
list = which(data$bef_neg!=0 & !is.na(data$bef_neg) & data$bef_neg == data$next_neg & data$c_neg != data$bef_neg)
data$c_neg[list] = data$bef_neg[list]
data$libemploi[list] = data$bef_lib[list]


# Changing grades variable
data$bef_neg  <-ave(data$c_neg, data$ident, FUN=shiftm1)
data$bef_neg2 <-ave(data$c_neg, data$ident, FUN=shiftm2)
data$next_neg <-ave(data$c_neg, data$ident, FUN=shift1)
data$next_neg2 <-ave(data$c_neg, data$ident, FUN=shift2)
data$change_neg_bef  <- ifelse(data$c_neg == data$bef_neg | data$c_neg == data$bef_neg2, 0, 1)
data$change_neg_next <- ifelse(data$c_neg == data$next_neg| data$c_neg == data$next_neg2, 0, 1)


# Ind libemploi 
data$ind_lib = ifelse(data$libemploi == '', 0, 1)
data$count_lib = ave(data$ind_lib, data$ident, FUN = sum)
data$bef_ind_lib <-ave(data$ind_lib, data$ident, FUN=shiftm1)
data$bef2_ind_lib <-ave(data$ind_lib, data$ident, FUN=shiftm2)
data$next_ind_lib <-ave(data$ind_lib, data$ident, FUN=shift1)
# Lib without AT
data$diff = data$count_lib - data$count_AT
# Ind missing echelon 
data$missing_ech = ifelse(is.na(data$echelon) & data$libemploi != '', 1, 0)
data$count_missing_ech = ave(data$missing_ech, data$ident, FUN = sum)


## Cleaned data
list3 = data$ident[which(data$c_neg == 0 & data$libemploi != '')]
list4 = data$ident[which(is.na(data$echelon) & is.element(data$c_neg, c(793, 794, 795, 796)))]
list5 = data$ident[which(data$ib > 0 & data$libemploi == '')]
list = unique(union(union(list3,list4), list5))
data_cleaned = data[which(!is.element(data$ident, list)),]

# Data
data -> data_all
data <- data_cleaned


#### II. Descriptive statistics ####



#### II.1 Sample selection ####

size_sample = matrix(ncol = 2, nrow = 4)

list1 = data_all$ident[which(data_all$statut != "" & data_all$libemploi == ''  & data_all$annee>= 2007)]
list2 = data_all$ident[which(data_all$c_neg == 0 & data_all$libemploi != '' & data_all$annee>= 2007)]
list3 = data_all$ident[which(is.na(data_all$echelon) & is.element(data_all$c_neg, c(793, 794, 795, 796))  & data_all$annee>= 2007)]

for (d in 1:4)
{
if (d == 1){dataset = data_all}
if (d == 2){dataset = dataset[-which(is.element(dataset$ident, list1)),]}
if (d == 3){dataset = dataset[-which(is.element(dataset$ident, list2)),]}
if (d == 4){dataset = dataset[-which(is.element(dataset$ident, list3)),]}
#size_sample[d,1] = length(dataset$ident)
#size_sample[d,2] = 100*length(dataset$ident)/size_sample[1,1]
size_sample[d,1] = length(unique(dataset$ident))
size_sample[d,2] = 100*length(unique(dataset$ident))/size_sample[1,1]
}

colnames(size_sample) <- c("Nb d'individus", "\\% echantillon initial")
rownames(size_sample) <- c("Echantillon initial",
                           "F1: Libemploi manquant quand statut non vide",
                           "F2: Neg manquant quand libemploi renseigné", "F3: Echelon manquant quand neg dans AT")
print(xtable(size_sample,align="l|cc",nrow = nrow(table), ncol=ncol(table)+1, byrow=T, digits=0),
      hline.after=c(0,1,4), sanitize.text.function=identity,size="\\footnotesize", only.contents=T)



#### II.2 Entry and exit neg ####


# Proportion of each type


# TODO: echelon d'entree, de sortie, duree passee dans le corps

list_neg = c(793, 794, 795, 796)
table_entry = matrix(ncol = length(list_neg), nrow = 9)
table_exit  = matrix(ncol = length(list_neg), nrow = 9)

data_entry = data[which(data$change_neg_bef ==1  & data$annee>2007),]
data_entry$bef_neg[which(data_entry$bef_neg == 0 & data_entry$lag_ind_lib == 1)] = 999
data_entry$bef_neg[which(data_entry$bef_neg == 0 & data_entry$lag_ind_lib == 0)] = 888

data_exit = data[which(data$change_neg_next ==1  & data$annee<2015),]
data_exit$next_neg[which(data_exit$next_neg == 0 & data_exit$next_ind_lib == 1)] = 999
data_exit$next_neg[which(data_exit$next_neg == 0 & data_exit$next_ind_lib == 0)] = 888

for (n in 1:length(list_neg))
{
list = which(data_entry$c_neg == list_neg[n]) 
# From AT neg
for (n2 in 1:length(list_neg))
{
list2 = which(data_entry$bef_neg == list_neg[n2])
table_entry[(n2),n] = length(intersect(list, list2))/length(list)  
}
# From other known neg
list3 = which(!is.element(data_entry$bef_neg, cbind(888, 999, list_neg)))
table_entry[5,n] = length(intersect(list, list3))/length(list)  
# From missing neg
list4 = which(data_entry$bef_neg == 999)
table_entry[6,n] = length(intersect(list, list4))/length(list)  
# From missing libemploi
list5 = which(data_entry$bef_neg == 888)
table_entry[7,n] = length(intersect(list, list5))/length(list)  
# Total: 
table_entry[8,n] = sum(table_entry[1:7,n])

## Exit
list = which(data_exit$c_neg == list_neg[n]) 
# To AT neg
for (n2 in 1:length(list_neg)){
list2 = which(data_exit$next_neg == list_neg[n2])
table_exit[(n2),n] = length(intersect(list, list2))/length(list)  
}
# To other known neg
list3 = which(!is.element(data_exit$next_neg, cbind(888, 999, list_neg)))
table_exit[5,n] = length(intersect(list, list3))/length(list)  
# To missing neg
list4 = which(data_exit$next_neg == 999)
table_exit[6,n] = length(intersect(list, list4))/length(list)  
# To missing libemploi
list5 = which(data_exit$next_neg == 888)
table_exit[7,n] = length(intersect(list, list5))/length(list)  
# Total: 
table_exit[8,n] = sum(table_exit[1:7,n])
}


colnames(table) <- c("AT2", "AT1", "ATP2", "ATP1")
rownames(table) <- c("Nb obs", "Libelle n-1 manquant", "NEG n-1 = AT2", "NEG n-1 = AT1", "NEG n-1 = ATP2", "NEG n-1 = ATP1",
                    "NEG n-1 = autres", "NEG n-1 = manquant", "total")
table<-desc
print(xtable(table,align="l|cccc",nrow = nrow(table), ncol=ncol(table)+1, byrow=T),
      hline.after=c(0,1,9), sanitize.text.function=identity,size="\\footnotesize", only.contents=T)



#### II.3 Distribution of time spent in corps and echelon ####


## Proba de quitter le corps par échelon (survival)
exit_rate = matrix(ncol = 11, nrow = 4)
surv_rate = matrix(ncol = 11, nrow = 4)

table(data_cleaned$echelon[which(data_cleaned$c_neg == 794)])
table(data_cleaned$echelon[which(data_cleaned$c_neg == 793)])

for (e in seq(1,11,1))
{
for (n in seq(1,4,1))
{
exit_rate[n, e] = length(which(data_cleaned$change_neg_next == 1 & data_cleaned$c_neg == list_neg[n] & data_cleaned$echelon == e))/ 
                  length(which(data_cleaned$c_neg == list_neg[n] & data_cleaned$echelon == e))
surv_rate[n, e] = length(which(data_cleaned$change_neg_bef == 0 & data_cleaned$c_neg == list_neg[n] & data_cleaned$echelon == e))/ 
                  length(which(data_cleaned$c_neg == list_neg[n] & data_cleaned$echelon == e))  
}
}




# Time spent in echelon and grade 
data$a = 1
data$count_neg     = ave(data$a, list(data$ident, data$c_neg), FUN = sum)
data$count_echelon = ave(data$a, list(data$ident, data$c_neg, data$echelon), FUN = sum)
# Change echlon
data$bef_ech  <-ave(data$echelon, list(data$ident, data$c_neg), FUN=shiftm1)
data$change_neg_next <- ifelse(data$c_neg == data$next_neg, 0, 1)



data_all = data[which(data$count_AT == 9 & data$count_lib == 9 & data$count_missing_ech == 0), ]

# Distribution de l'echelon a l'entre dans corps
entry_echelon_AT2 = data$echelon[which(data$change_neg_bef2 ==1  & 
                                       data$c_neg == list_neg[1] & 
                                       data$annee > 2008)] 

View(data[which(is.element(data$ident, data$ident[which(data$change_neg_bef ==1  & 
                                                          data$c_neg == list_neg[1] & 
                                                          data$annee > 2008)])),])

View(data[which(is.element(data$ident, data$ident[which(data$change_neg_bef2 ==1  &
                           data$bef_ind_lib == 0 & data$bef2_ind_lib == 0 &                               
                           data$c_neg == list_neg[1] & data$annee > 2008)])),])
                  
                  
table(entry_echelon_AT2)

#### II.3 Distribution of destination when eligible ####



### Grid graphes: ###
# Sous pop: toute carriere dans AT, 100 individus. 


list_drop = unique(data_cleaned$ident[which(data_cleaned$c_neg != 0 & !is.element(data_cleaned$c_neg, list_neg))])
list_keep = unique(data_cleaned$ident[which(data_cleaned$count_AT >= 8 & data_cleaned$count == data_cleaned$count_AT )])

list = setdiff(list_keep, list_drop)
sub = sample(list , 100)
sub_data = data_cleaned[which(is.element(data_cleaned$ident, sub) & data_cleaned$annee > 2006), c("ident", "c_neg", "ib", "annee", "count_AT", "first_AT")]
sub_data$bef_neg  <-ave(sub_data$c_neg, sub_data$ident, FUN=shiftm1)
sub_data$change_neg_bef  <- ifelse(sub_data$c_neg == sub_data$bef_neg, 0, 1)
sub_data$ib_change <- sub_data$change_neg_bef*sub_data$ib
sub_data$ib_change[sub_data$first_AT == 1] = 0


data1 = sub_data[, c("ident", 'annee', "ib")]; data1$indice = data1$ib
data2 = sub_data[, c("ident", 'annee', "ib_change")]; data2$indice = data2$ib_change
lim = range(data1$ib[data1$ib>0])

pdf(paste0(fig_path,"trajectoires.pdf"))
ggplot(data = data1, aes(x = annee, y = indice)) + geom_line() + geom_point(data=data2, shape = 21, fill = "red")+
  ylim(lim[1], lim[2]) + facet_wrap(~ident) + 
theme(strip.background = element_blank(), strip.text = element_blank(), axis.text.x=element_blank())
dev.off()


