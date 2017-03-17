######################################################################################################################## 
######################################## TRAJECTORIES in ADJOINT TECHNIQUE CORPS ######################################
######################################################################################################################## 


#### 0. Initialisation ####


# path
place = "mac"
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
mainAT = read.csv(paste0(data_path,"corpsAT.csv"))
list_neg_AT = c(793, 794, 795, 796)
sub_data_AT = mainAT[which(is.element(mainAT$ident, sample(unique(mainAT$ident), 10000))), ]

mainAA = read.csv(paste0(data_path,"corpsAA.csv"))
list_neg_AA = c(791, 792, 0014, 0162)
sub_data_AA = mainAA[which(is.element(mainAA$ident, sample(unique(mainAA$ident), 10000))), ]

mainES = read.csv(paste0(data_path,"corpsES.csv"))
list_neg_ES = c(791, 792, 0014, 0162)
sub_data_ES = mainAA[which(is.element(mainES$ident, sample(unique(mainES$ident), 10000))), ]



#### I. WOD ####

data_wod <- function(data, list_neg) 
{
  data$libemploi = as.character(data$libemploi)
  data$c_neg = as.numeric(format(data$c_neg))
  data$c_neg[which(is.na(data$c_neg))] <- 0
  data$echelon = data$echelon4
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
  data = slide(data, "libemploi", GroupVar = "ident", NewVar = "bef_lib2", slideBy = -2,
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
  data$change_neg_bef  <- ifelse(data$c_neg == data$bef_neg , 0, 1)
  data$change_neg_next <- ifelse(data$c_neg == data$next_neg, 0, 1)
  
  data$bef_ech  <-ave(data$echelon4, data$ident, FUN=shiftm1)
  data$next_ech <-ave(data$echelon4, data$ident, FUN=shift1)
  
  # Ind libemploi 
  data$ind_lib = ifelse(data$libemploi == '', 0, 1)
  data$count_lib = ave(data$ind_lib, data$ident, FUN = sum)
  data$bef_ind_lib  <- ave(data$ind_lib, data$ident, FUN=shiftm1)
  data$bef2_ind_lib <- ave(data$ind_lib, data$ident, FUN=shiftm2)
  data$next_ind_lib <- ave(data$ind_lib, data$ident, FUN=shift1)
  # Lib without AT
  data$diff = data$count_lib - data$count_AT
  # Ind missing echelon 
  data$missing_ech = ifelse(is.na(data$echelon) & data$libemploi != '', 1, 0)
  data$count_missing_ech = ave(data$missing_ech, data$ident, FUN = sum)
  
  return(data)
}

data_clean <- function(data, list_neg)
{
  list1 = data$ident[which(data$statut != '' & data$libemploi == '')]
  list2 = data$ident[which(data$c_neg == 0 & data$libemploi != '')]
  list3 = data$ident[which(is.na(data$echelon4) & is.element(data$c_neg, list_neg))]
  list = unique(union(union(list1,list2), list3))
  data_cleaned = data[which(!is.element(data$ident, list)),]  
  return(data_cleaned)
}
  
# Data
data_all_AT   <- data_wod(data = mainAT, list_neg = list_neg_AT)
data_clean_AT <- data_clean(data_all_AT, list_neg_AT)

data_all_AA   <- data_wod(data = mainAA, list_neg = list_neg_AA)
data_clean_AA <- data_clean(data_all_AA, list_neg_AA)


#### II. Descriptive statistics ####

### II.1 Sample selection ###

size_sample = matrix(ncol = 2, nrow = 4)

list1 = data_all$ident[which(data_all$statut != "" & data_all$libemploi == ''  & data_all$annee>= 2007)]
list2 = data_all$ident[which(data_all$c_neg == 0 & data_all$libemploi != '' & data_all$annee>= 2007)]
list3 = data_all$ident[which(is.na(data_all$echelon) & is.element(data_all$c_neg, c(793, 794, 795, 796))  & data_all$annee>= 2007)]


length(which(is.na(data_all$echelon) & is.element(data_all$c_neg, c(793, 794, 795, 796))))/ length(which(is.element(data_all$c_neg, c(793, 794, 795, 796))))
length(which(is.na(data_all$echelon) & is.element(data_all$c_neg, c(793))))/ length(which(is.element(data_all$c_neg, c(793))))
length(which(is.na(data_all$echelon) & is.element(data_all$c_neg, c(794))))/ length(which(is.element(data_all$c_neg, c(794))))
length(which(is.na(data_all$echelon) & is.element(data_all$c_neg, c(795))))/ length(which(is.element(data_all$c_neg, c(795))))
length(which(is.na(data_all$echelon) & is.element(data_all$c_neg, c(796))))/ length(which(is.element(data_all$c_neg, c(796))))

for (d in 1:3)
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
                           "F2: Neg manquant quand libemploi renseign?", "F3: Echelon manquant quand neg dans AT")
print(xtable(size_sample,align="l|cc",nrow = nrow(table), ncol=ncol(table)+1, byrow=T, digits=0),
      hline.after=c(0,1,4), sanitize.text.function=identity,size="\\footnotesize", only.contents=T)


### II.2 Qualite des donness  ###

# Qualite: proportion des missing echelon par annee
list_neg = list_neg_AT
years = 2007:2015
missing = matrix(ncol = 6, nrow = length(years))
for (y in 1:length(years))
{
data1 = data_all_AT[which(data_all_AT$annee == years[y]), ]
missing[y,1] =  length(which(data1$c_neg == 0 & data1$libemploi != ''))/length(which(data1$libemploi != ''))
missing[y,2] =  length(which(is.na(data1$echelon4) & data1$c_neg != 0))/length(which(data1$c_neg != 0))  
missing[y,3] =  length(which(is.na(data1$echelon4) & data1$c_neg == list_neg[1]))/length(which(data1$c_neg == list_neg[1]))  
missing[y,4] =  length(which(is.na(data1$echelon4) & data1$c_neg == list_neg[2]))/length(which(data1$c_neg == list_neg[2]))  
missing[y,5] =  length(which(is.na(data1$echelon4) & data1$c_neg == list_neg[3]))/length(which(data1$c_neg == list_neg[3]))  
missing[y,6] =  length(which(is.na(data1$echelon4) & data1$c_neg == list_neg[4]))/length(which(data1$c_neg == list_neg[4]))  
}

colnames(missing) <- c("\\% c_neg (libemploi ", "\\% ech NA", 
                     "\\% ech NA AT2 ", "\\% ech NA AT1 ", "\\% ech NA ATP2 ", "\\% ech NA ATP1 ")
rownames(missing) <- years
table = missing
print(xtable(table,align="l|cccccc",nrow = nrow(table), ncol=ncol(table)+1, byrow=T),
      sanitize.text.function=identity,size="\\footnotesize", only.contents=T)

# Passage de 2010 à 2011
years = 2008:2015
evo = matrix(ncol = length(years), nrow = 4)
for (y in 1:length(years))
{
data1 = data_all_AT[which(data_all_AT$annee == years[y]), ]
data2 = data1[which(data1$bef_neg != 0), ]
data3 = data1[which(data1$bef_neg != 0 & data1$c_neg != 0), ]
denom = length(data1$change_neg_bef) 
evo[1, y] = length(which(data1$change_neg_bef == 1))/denom
evo[2, y] = length(which(data1$change_neg_bef == 1 & data1$bef_neg == 0))/denom
evo[3, y] = length(which(data1$change_neg_bef == 1 & data1$c_neg == 0))/denom
evo[4, y] = length(which(data1$change_neg_bef == 1 & data1$c_neg != 0 & data1$bef_neg  != 0))/denom
}
colnames(evo) <- years
rownames(evo) <- c("% changement de grade", "% chgt avec NA en n-1",
                   "% chgt avec NA en n", "Chgt de grade à grade")
table = evo
print(xtable(table,align="ccccccccc",nrow = nrow(table), ncol=ncol(table)+1, byrow=T),
     sanitize.text.function=identity,size="\\footnotesize", only.contents=T)

# Baisse échelon dans meme grade
list = which(is.element(data$c_neg, list_neg) &
             data$c_neg == data$next_neg & 
             !is.na(data$echelon4) & !is.na(data$next_ech) & 
              data$echelon4>0 & data$next_ech>0 & 
              data$echelon4>data$next_ech)

View(data_cleaned[list, c('ident', 'annee', 'c_neg', 'echelon', 'next_neg', 'next_neg2', 'bef_neg', 'bef_neg2', 'change_neg_next', 'change_neg_next')])

# Dispersion des erreurs entre individus


#### III. Statistiques descriptives ####

# Proportion of each type

list1 = data_all_AT$ident[which(data_all_AT$statut != '' & data_all_AT$libemploi == '')]
list2 = data_all_AT$ident[which(data_all_AT$c_neg == 0 & data_all_AT$libemploi != '')]
data_clean =  data_all_AT[which(!is.element(data_all_AT$ident, union(list1,list2))),]  

t = table(data_clean[which(data_clean$c_neg == 793 & data_clean$change_neg_next == 1 & 
                           data_clean$annee >= 2011 & data_clean$annee < 2015),"next_neg"])
t / length(data_clean[which(data_clean$c_neg == 793 & data_clean$change_neg_next == 1 & 
                            data_clean$annee >= 2011 & data_clean$annee < 2015),"next_neg"])
# TODO: echelon d'entree, de sortie, duree passee dans le corps

list_neg = c(793, 794, 795, 796)
table_entry = matrix(ncol = length(list_neg), nrow = 7)
table_exit  = matrix(ncol = length(list_neg), nrow = 7)

data_entry = data[which(data$change_neg_bef ==1  & data$annee >= 2012),]
data_exit = data[which(data$change_neg_next ==1  & data$annee >= 2011 & data$annee < 2015),]

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
list3 = which(!is.element(data_entry$bef_neg, cbind(0, list_neg)))
table_entry[5,n] = length(intersect(list, list3))/length(list)  
# From missing neg
list4 = which(data_entry$bef_neg == 0)
table_entry[6,n] = length(intersect(list, list4))/length(list)  
# Total: 
table_entry[7,n] = sum(table_entry[1:6,n])

## Exit
list = which(data_exit$c_neg == list_neg[n]) 
# To AT neg
for (n2 in 1:length(list_neg)){
list2 = which(data_exit$next_neg == list_neg[n2])
table_exit[(n2),n] = length(intersect(list, list2))/length(list)  
}
# To other known neg
list3 = which(!is.element(data_exit$next_neg, cbind(0, list_neg)))
table_exit[5,n] = length(intersect(list, list3))/length(list)  
# From missing neg
list4 = which(data_exit$next_neg == 0)
table_exit[6,n] = length(intersect(list, list4))/length(list)  
table_exit[7,n] = sum(table_exit[1:6,n])
}

table = table_entry*100
colnames(table) <- c("AT2", "AT1", "ATP2", "ATP1")
rownames(table) <- c("NEG n-1 = AT1", "NEG n-1 = AT2", "NEG n-1 = ATP2", "NEG n-1 = ATP1",
                    "NEG n-1 = autres", "NEG n-1 = manquant", "total")
print(xtable(table,align="l|cccc",nrow = nrow(table), ncol=ncol(table)+1, byrow=T),
     sanitize.text.function=identity,size="\\footnotesize", only.contents=T)

table = table_exit*100
colnames(table) <- c("AT2", "AT1", "ATP2", "ATP1")
rownames(table) <- c("NEG n+1 = AT1", "NEG n+1 = AT2", "NEG n+1 = ATP2", "NEG n+1 = ATP1",
                     "NEG n+1 = autres", "NEG n+1 = manquant", "total")
print(xtable(table,align="l|cccc",nrow = nrow(table), ncol=ncol(table)+1, byrow=T),
      sanitize.text.function=identity,size="\\footnotesize", only.contents=T)


#### II.2 Retrouver graphe PJ (proba de sortir selon echelon pour une ann?e donn?e) ####
list1 = data_all_AT$ident[which(data_all_AT$statut != '' & data_all_AT$libemploi == '')]
list2 = data_all_AT$ident[which(data_all_AT$c_neg == 0 & data_all_AT$libemploi != '')]
data_clean =  data_all_AT[which(!is.element(data_all_AT$ident, union(list1,list2))),]  

data = data_clean[which(data_clean$c_neg == 793 & 
                        data_clean$annee >= 2011 & data_clean$annee <= 2014),]

table(data$echelon4)/length(data$echelon4)
table(data$echelon4[which(data$change_neg_next==1)])/length(data$echelon4[which(data$change_neg_next==1)])
table(data$echelon4[which(data$next_neg == 794)])/length(data$echelon4[which(data$next_neg == 794)])

data = data_clean[which(data_clean$c_neg == 794 & 
                          data_clean$annee >= 2011 & data_clean$annee <= 2014),]

table(data$echelon4)/length(data$echelon4)
table(data$echelon4[which(data$change_neg_next==1)])/length(data$echelon4[which(data$change_neg_next==1)])
table(data$echelon4[which(data$next_neg == 795)])/length(data$echelon4[which(data$next_neg == 794)])

#### II.3 Distribution of time spent in corps and echelon ####

## Proba de quitter le corps par echelon (survival)
exit_rate  = matrix(ncol = 11, nrow = 4)
surv_rate  = matrix(ncol = 11, nrow = 4)
exit_rate2 = matrix(ncol = 11, nrow = 4)
surv_rate2 = matrix(ncol = 11, nrow = 4)

table(data_cleaned$echelon[which(data_cleaned$c_neg == 794)])
table(data_cleaned$echelon[which(data_cleaned$c_neg == 793)])


for (e in seq(1,11,1))
{
for (n in seq(1,4,1))
{
exit_rate[n, e] = length(which(data_cleaned$c_neg == list_neg[n] & data_cleaned$echelon == e & data_cleaned$annee<2015 & data_cleaned$change_neg_next == 1 ))/ 
                  length(which(data_cleaned$c_neg == list_neg[n] & data_cleaned$echelon == e & data_cleaned$annee<2015))
surv_rate[n, e] = length(which(data_cleaned$c_neg == list_neg[n] & data_cleaned$echelon == e & data_cleaned$annee>2007 & data_cleaned$change_neg_bef == 1 ))/ 
                  length(which(data_cleaned$c_neg == list_neg[n] & data_cleaned$echelon == e & data_cleaned$annee>2007))  
exit_rate2[n, e] = length(which(data_cleaned$c_neg == list_neg[n] & data_cleaned$echelon == e & data_cleaned$annee>2011 & data_cleaned$annee<2015 & data_cleaned$change_neg_next == 1 ))/ 
                   length(which(data_cleaned$c_neg == list_neg[n] & data_cleaned$echelon == e  & data_cleaned$annee>2011 & data_cleaned$annee<2015))
surv_rate2[n, e] = length(which(data_cleaned$c_neg == list_neg[n] & data_cleaned$echelon == e & data_cleaned$annee>2007 & data_cleaned$change_neg_bef == 1 ))/ 
                   length(which(data_cleaned$c_neg == list_neg[n] & data_cleaned$echelon == e & data_cleaned$annee>2007))  
}
}

View(data_cleaned[, c('ident', 'annee', 'c_neg', 'echelon1', 'echelon4', 'ib', 'next_neg', 'next_neg2', 'bef_neg', 'bef_neg2', 'change_neg_next', 'change_neg_next')])


# Time spent in echelon and grade 
data$a = 1
data$count_neg     = ave(data$a, list(data$ident, data$c_neg), FUN = sum)
data$count_echelon = ave(data$a, list(data$ident, data$c_neg, data$echelon), FUN = sum)
# Change echlon
data$bef_ech  <-ave(data$echelon, list(data$ident, data$c_neg), FUN=shiftm1)
data$change_neg_next <- ifelse(data$c_neg == data$next_neg, 0, 1)



data_all = data[which(data$count_AT == 9 & data$count_lib == 9 & data$count_missing_ech == 0), ]

# Distribution de l'echelon a l'entre dans corps

entry_echelon_AT2 = data$echelon[which(data$change_neg_bef ==1  & 
                                       data$c_neg == list_neg[1] & 
                                       data$annee > 2012)] 
entry_echelon_AT1 = data$echelon[which(data$change_neg_bef ==1  & 
                                         data$c_neg == list_neg[2] & 
                                         data$annee > 2012)] 
entry_echelon_ATP2 = data$echelon[which(data$change_neg_bef ==1  & 
                                         data$c_neg == list_neg[3] & 
                                         data$annee > 2012)] 
entry_echelon_ATP1 = data$echelon[which(data$change_neg_bef ==1  & 
                                          data$c_neg == list_neg[4] & 
                                          data$annee > 2012)] 

View(data[which(is.element(data$ident, data$ident[which(data$change_neg_bef ==1  & 
                                                          data$c_neg == list_neg[1] & 
                                                          data$annee > 2008)])),])

View(data[which(is.element(data$ident, data$ident[which(data$change_neg_bef2 ==1  &
                           data$bef_ind_lib == 0 & data$bef2_ind_lib == 0 &                               
                           data$c_neg == list_neg[1] & data$annee > 2008)])),])
                  
table(entry_echelon_AT2)
table(entry_echelon_AT1)
table(entry_echelon_ATP2)
table(entry_echelon_ATP1)



#### III. Survival analysis ####

#### III.1 Grade only ####

list_neg = c(793, 794, 795, 796)

for (c in c('AA', 'AT'))
{
if (c == 'AT'){data_all = data_all_AT; list_neg = list_neg_AT}
if (c == 'AA'){data_all = data_all_AA; list_neg = list_neg_AA}
if (c == 'ES'){data_all = data_all_ES; list_neg = list_neg_ES}  
  

list1 = data_all$ident[which(data_all$c_neg == 0 & data_all$libemploi != '')]
list2 = data_all$ident[which(data_all$statut != '' & data_all$libemploi == '')]

list = unique((union(list1,list2)))
data = data_all[which(!is.element(data_all$ident, list)),]

years = 2008:2015
surv_1     = matrix(nrow = length(years), ncol = length(years))
surv_rel_1 = matrix(nrow = length(years), ncol = length(years))

surv = array(dim = c(length(list_neg), length(years), ncol = length(years)))
surv_rel = array(dim = c(length(list_neg), length(years), ncol = length(years)))

for (n in 1: length(list_neg))
{
for (y in 1:length(years))
{
list_keep1 = unique(data$ident[which(data$change_neg_bef == 1 & data$c_neg == list_neg[n] & data$annee == years[y])])  
#list_keep1 = unique(data$ident[which(data$bef_lib == '' & data$bef_lib2 == '' & data$c_neg == list_neg[n] & data$annee == years[y])])  
sub_data = data[which(is.element(data$ident, list_keep1) & data$annee >= years[y]), c("ident", "annee", "c_neg", "echelon", "libemploi", "change_neg_bef", "change_neg_next")]  
sub_data$cum_sum_change = ave(sub_data$change_neg_bef, sub_data$ident, FUN= cumsum)
sub_data = sub_data[which(sub_data$cum_sum_change <= 1),]
sub_data$cum_sum_change = ave(sub_data$change_neg_bef, sub_data$ident, FUN= cumsum)
sub_data$a = 1
sub_data$count_neg     = ave(sub_data$a, list(sub_data$ident, sub_data$c_neg), FUN = sum)
data_ind  <- sub_data[which(!duplicated(sub_data$ident)),]

count = length(data_ind$ident)
for (t in y:length(years))
{
  surv[n, y, t] = count
  surv_rel[n, y, t] = 100*count/length(data_ind$ident)
  count = count - length(which(data_ind$count_neg == t - y + 1))  
}
}
  pdf(paste0(fig_path,"survival_",c,"_",n,".pdf"))
  n_col <- colorRampPalette(c("black", "grey80"))(length(years)) 
  type = rep(c(1,2),5)
  layout(matrix(c(1, 2, 3), nrow=3,ncol=1, byrow=TRUE), heights=c(3, 3,1))
  par(mar=c(4.1,4.1,0.2,0.2))
  # Nb
  table = surv[1, ,]
  plot  (years,rep(NA,length(years)),ylim=c(min(table, na.rm = T),max(table, na.rm = T)),ylab="Nb d'individus",xlab="Annee")
  for (a in 1:length(years))
  {
    lines(years,table[a, ],col=n_col[a],lwd=3, lty = type[a]) 
  }
  # %
  table = surv_rel[1, ,]
  plot  (years,rep(NA,length(years)),ylim=c(min(table, na.rm = T),max(table, na.rm = T)),ylab="% d'individus",xlab="Annee")
  for (a in 1:length(years))
  {
    lines(years,table[a, ],col=n_col[a],lwd=3, lty = type[a]) 
  }
  
  par(mar=c(0,0,0,0),font=1.5)
  plot.new()
  legend("center",legend=years, title = "Annee d'entree dans le grade:",
         col=n_col,lty=type[1:length(years)],lwd=3,cex=1.3, ncol=4, bty = "n")
  dev.off()
  
  
  
}
}

#### III.1.2 First  ####



  data_all = data_all_AT
  list_neg = list_neg_AT
  
  
  list1 = data_all$ident[which(data_all$c_neg == 0 & data_all$libemploi != '')]
  list2 = data_all$ident[which(data_all$statut != '' & data_all$libemploi == '')]
  list = unique((union(list1,list2)))
  data = data_all[which(!is.element(data_all$ident, list)),]
  
  data = data_clean_AT
  
  years = c(2010:2015)
  state =     matrix(nrow = 4, ncol = length(years))
  state_rel = matrix(nrow = 4, ncol = length(years))
  state_rel_elig = matrix(nrow = 4, ncol = length(years))
  state_rel_noelig = matrix(nrow = 4, ncol = length(years))

  list_keep1 = unique(data$ident[which(data$c_neg == list_neg[1] & data$annee == 2009 & data$an_aff == 2009)]) 
 # list_keep1 = unique(data$ident[which(data$bef_lib == '' & data$bef_lib2 == '' & data$c_neg == list_neg[1] & data$annee == 2007)])  
  sub_data = data[which(is.element(data$ident, list_keep1) & data$annee >= 2009), c("ident", "annee", "c_neg", "bef_neg", "echelon", "echelon4", "libemploi", "change_neg_bef", "change_neg_next")] 
  sub_data$bef_ech = ave(sub_data$echelon4, sub_data$ident, FUN=shiftm1)
  
  
  table(data$echelon[which(data$annee == 2007)])
  
  for (y in 1:length(years))
  {
  stayers =  sub_data$ident[which(sub_data$bef_neg == list_neg[1] & sub_data$annee == years[y])]
  stayers_elig =  sub_data$ident[which(sub_data$bef_neg == list_neg[1] & sub_data$annee == years[y] &   sub_data$bef_ech>=3 )]
  stayers_noelig =  sub_data$ident[which(sub_data$bef_neg == list_neg[1] & sub_data$annee == years[y] &   sub_data$bef_ech<3 &   sub_data$bef_ech>0 )]
  sub_data  =  sub_data[which(is.element(sub_data$ident, stayers)), ]
  sub_data_el  =  sub_data[which(is.element(sub_data$ident, stayers_elig)), ]
  sub_data_noel  =  sub_data[which(is.element(sub_data$ident, stayers_noelig)), ]
  state[1, y] = length(which(sub_data$c_neg == list_neg[1]& sub_data$annee == years[y]))
  state[2, y] = length(which(sub_data$c_neg == list_neg[2]& sub_data$annee == years[y]))
  state[3, y] = length(which(!is.element(sub_data$c_neg, c(0, list_neg[1], list_neg[2])) & sub_data$annee == years[y] ))
  state[4, y] = length(which(sub_data$c_neg == 0 & sub_data$annee == years[y]))
  state_rel[, y] = state[, y]/length(stayers)
  # Elig
  state_rel_elig[1, y] = length(which(sub_data_el$c_neg == list_neg[1]& sub_data_el$annee == years[y]))/length(stayers_elig)
  state_rel_elig[2, y] = length(which(sub_data_el$c_neg == list_neg[2]& sub_data_el$annee == years[y]))/length(stayers_elig)
  state_rel_elig[3, y] = length(which(!is.element(sub_data_el$c_neg, c(0, list_neg[1], list_neg[2])) & sub_data_el$annee == years[y] ))/length(stayers_elig)
  state_rel_elig[4, y] = length(which(sub_data_el$c_neg == 0 & sub_data_el$annee == years[y]))/length(stayers_elig)
  # noelig
  state_rel_noelig[1, y] = length(which(sub_data_noel$c_neg == list_neg[1]& sub_data_noel$annee == years[y]))/length(stayers_noelig)
  state_rel_noelig[2, y] = length(which(sub_data_noel$c_neg == list_neg[2]& sub_data_noel$annee == years[y]))/length(stayers_noelig)
  state_rel_noelig[3, y] = length(which(!is.element(sub_data_noel$c_neg, c(0, list_neg[1], list_neg[2])) & sub_data_noel$annee == years[y] ))/length(stayers_noelig)
  state_rel_noelig[4, y] = length(which(sub_data_noel$c_neg == 0 & sub_data_noel$annee == years[y]))/length(stayers_noelig)
  }  
  
  
  pdf(paste0(fig_path,"destination_",c,"_1.pdf"))
  par(mar=c(4.1,4.1,0.2,0.2))
  barplot(state_rel, names.arg = years, 
          legend = c("Meme NEG", "Sortie NEG suivant", "Sortie autre NEG", "Sortie NA"), 
          args.legend = list(x = "bottomright"))
  dev.off() 
  

  barplot(state_rel_elig, names.arg = years, 
          legend = c("Meme NEG", "Sortie NEG suivant", "Sortie autre NEG", "Sortie NA"), 
          args.legend = list(x = "bottomright"))
  barplot(state_rel_noelig, names.arg = years, 
          legend = c("Meme NEG", "Sortie NEG suivant", "Sortie autre NEG", "Sortie NA"), 
          args.legend = list(x = "bottomright"))
  
}  
  
  
      
      sub_data = sub_data[which(sub_data$cum_sum_change <= 1),]
      sub_data$cum_sum_change = ave(sub_data$change_neg_bef, sub_data$ident, FUN= cumsum)
      sub_data$a = 1
      sub_data$count_neg     = ave(sub_data$a, list(sub_data$ident, sub_data$c_neg), FUN = sum)
      data_ind  <- sub_data[which(!duplicated(sub_data$ident)),]
      
      count = length(data_ind$ident)
      for (t in y:length(years))
      {
        surv[n, y, t] = count
        surv_rel[n, y, t] = 100*count/length(data_ind$ident)
        count = count - length(which(data_ind$count_neg == t - y + 1))  
      }
    }
    pdf(paste0(fig_path,"survival_",c,"_",n,".pdf"))
    n_col <- colorRampPalette(c("black", "grey80"))(length(years)) 
    type = rep(c(1,2),5)
    layout(matrix(c(1, 2, 3), nrow=3,ncol=1, byrow=TRUE), heights=c(3, 3,1))
    par(mar=c(4.1,4.1,0.2,0.2))
    # Nb
    table = surv[1, ,]
    plot  (years,rep(NA,length(years)),ylim=c(min(table, na.rm = T),max(table, na.rm = T)),ylab="Nb d'individus",xlab="Annee")
    for (a in 1:length(years))
    {
      lines(years,table[a, ],col=n_col[a],lwd=3, lty = type[a]) 
    }
    # %
    table = surv_rel[1, ,]
    plot  (years,rep(NA,length(years)),ylim=c(min(table, na.rm = T),max(table, na.rm = T)),ylab="% d'individus",xlab="Annee")
    for (a in 1:length(years))
    {
      lines(years,table[a, ],col=n_col[a],lwd=3, lty = type[a]) 
    }
    
    par(mar=c(0,0,0,0),font=1.5)
    plot.new()
    legend("center",legend=years, title = "Annee d'entree dans le grade:",
           col=n_col,lty=type[1:length(years)],lwd=3,cex=1.3, ncol=4, bty = "n")
    dev.off()
}




# Time spent in the grade
data = data1

time = seq(2007, 2015, 1)
surv = numeric(length(time))
count = length(data_ind$ident)
for (t in 1:length(time))
{
surv[t] = count
count = count - length(which(data_ind$count_neg == t))  
}
plot(time, surv, ylim = c(0, length(data_ind$ident)))


#### II.3 Distribution of destination when eligible ####


# Distribution of next grade by echelon 
list1 = data_all_AT$ident[which(data_all_AT$statut != '' & data_all_AT$libemploi == '')]
list2 = data_all_AT$ident[which(data_all_AT$c_neg == 0 & data_all_AT$libemploi != '')]
data_clean =  data_all_AT[which(!is.element(data_all_AT$ident, union(list1,list2))),]  


# AT2
distrib_next_AT2 = matrix(ncol = 4, nrow = 12)

data = data_clean[which(data_clean$c_neg == list_neg_AT[1] & 
                          data_clean$annee >= 2011 & data_clean$annee <= 2014),]
data$ind_stay  = ifelse(data$next_neg == data$c_neg, 1, 0) 
data$ind_exit1 = ifelse(data$next_neg == list_neg_AT[2], 1, 0) 
data$ind_exit2 = ifelse(data$next_neg == 0, 1, 0) 
data$ind_exit3 = ifelse(!is.element(data$next_neg,c(0, list_neg_AT[1], list_neg_AT[2])), 1, 0) 

distrib_next_AT2[,1] = aggregate(data$ind_stay, list(data$echelon4), FUN = mean, na.rm = F)$x
distrib_next_AT2[1,1] = mean(data$ind_stay[which(is.na(data$echelon4))])
distrib_next_AT2[,2] = aggregate(data$ind_exit1, list(data$echelon4), FUN = mean, na.rm = F)$x
distrib_next_AT2[1,2] = mean(data$ind_exit1[which(is.na(data$echelon4))])
distrib_next_AT2[,3] = aggregate(data$ind_exit2, list(data$echelon4), FUN = mean, na.rm = F)$x
distrib_next_AT2[1,3] = mean(data$ind_exit2[which(is.na(data$echelon4))])
distrib_next_AT2[,4] = aggregate(data$ind_exit3, list(data$echelon4), FUN = mean, na.rm = F)$x
distrib_next_AT2[1,4] = mean(data$ind_exit3[which(is.na(data$echelon4))])

n_col = c("black", "grey40", "grey60", "grey80") 
pdf(paste0(fig_path,"next_AT2.pdf"))
layout(matrix(c(1, 2), nrow=2,ncol=1, byrow=TRUE), heights=c(5,1))
par(mar=c(3,3,1,1))
barplot(t(distrib_next_AT2), col = n_col,
        names.arg = c("NA", seq(1,11,1)), ylim = c(0.5, 1), xpd = FALSE,
        args.legend = list(x = "bottomright"))
par(mar=c(0,0,0,0),font=1.5)
plot.new()
legend("center",legend=c("AT2", "AT1", "Manquant", "Autre"), title = "Grade à l'année suivante :",
       fill= n_col, cex=1, ncol = 4, bty = "n")
dev.off() 



# AT2
distrib_next_AT1 = matrix(ncol = 4, nrow = 13)

data = data_clean[which(data_clean$c_neg == list_neg_AT[2] & 
                          data_clean$annee >= 2011 & data_clean$annee <= 2014),]
data$ind_stay  = ifelse(data$next_neg == data$c_neg, 1, 0) 
data$ind_exit1 = ifelse(data$next_neg == list_neg_AT[3], 1, 0) 
data$ind_exit2 = ifelse(data$next_neg == 0, 1, 0) 
data$ind_exit3 = ifelse(!is.element(data$next_neg,c(0, list_neg_AT[2], list_neg_AT[3])), 1, 0) 

distrib_next_AT1[,1] = aggregate(data$ind_stay, list(data$echelon4), FUN = mean, na.rm = F)$x
distrib_next_AT1[1,1] = mean(data$ind_stay[which(is.na(data$echelon4))])
distrib_next_AT1[,2] = aggregate(data$ind_exit1, list(data$echelon4), FUN = mean, na.rm = F)$x
distrib_next_AT1[1,2] = mean(data$ind_exit1[which(is.na(data$echelon4))])
distrib_next_AT1[,3] = aggregate(data$ind_exit2, list(data$echelon4), FUN = mean, na.rm = F)$x
distrib_next_AT1[1,3] = mean(data$ind_exit2[which(is.na(data$echelon4))])
distrib_next_AT1[,4] = aggregate(data$ind_exit3, list(data$echelon4), FUN = mean, na.rm = F)$x
distrib_next_AT1[1,4] = mean(data$ind_exit3[which(is.na(data$echelon4))])

n_col = c("black", "grey40", "grey60", "grey80") 
pdf(paste0(fig_path,"next_AT1.pdf"))
layout(matrix(c(1, 2), nrow=2,ncol=1, byrow=TRUE), heights=c(5,1))
par(mar=c(3,3,1,1))
barplot(t(distrib_next_AT1), col = n_col,
        names.arg = c("NA", seq(1,12,1)), ylim = c(0.5, 1), xpd = FALSE,
        args.legend = list(x = "bottomright"))
par(mar=c(0,0,0,0),font=1.5)
plot.new()
legend("center",legend=c("AT1", "ATP2", "Manquant", "Autre"), title = "Grade à l'année suivante :",
       fill= n_col, cex=1, ncol = 4, bty = "n")
dev.off() 

t = table(data_clean[which(data_clean$c_neg == 794 & data_clean$change_neg_next == 1 & data_clean$echelon4 == 2 &
                             data_clean$annee >= 2011 & data_clean$annee < 2015),"next_neg"])
t / length(data_clean[which(data_clean$c_neg == 794 & data_clean$change_neg_next == 1 & data_clean$echelon4 == 2 & 
                              data_clean$annee >= 2011 & data_clean$annee < 2015),"next_neg"])

# => A 80% ces départs vers "autres grades" correspondent à des départs vers le AT2 => bizarre!

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


