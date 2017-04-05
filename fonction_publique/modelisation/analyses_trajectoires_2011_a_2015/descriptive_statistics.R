######################################################################################################################## 
############################## TRAJECTORIES in ADJOINT TECHNIQUE CORPS 2011 -2015 ######################################
######################################################################################################################## 


#### 0. Initialisation ####

data_path = "M:/CNRACL/output/"
git_path =  'C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/'

tab_path = paste0(git_path,"ecrits/note_1_Lisa/Tables/")
grille_path = paste0(git_path, "")

### Loading packages and functions ###
source(paste0(git_path, 'modelisation/OutilsCNRACL.R'))

# Read csv
mainAT = read.csv(paste0(data_path,"corpsAT_2011_2015.csv"))
mainAT2 = read.csv(paste0(data_path,"corpsAT.csv"))
list_neg_AT = c(793, 794, 795, 796)
sub_data_AT = mainAT[which(is.element(mainAT$ident, sample(unique(mainAT$ident), 10000))), ]

# mainAA = read.csv(paste0(data_path,"corpsAA_2011_2015.csv"))
# list_neg_AA = c(791, 792, 0014, 0162)
# sub_data_AA = mainAA[which(is.element(mainAA$ident, sample(unique(mainAA$ident), 10000))), ]
# 
# mainAS = read.csv(paste0(data_path,"corpsAS_2011_2015.csv"))
# list_neg_AS = c(840, 841, 842, 0162)
# sub_data_AS = mainAS[which(is.element(mainAS$ident, sample(unique(mainAS$ident), 10000))), ]

get_list_neg <- function(corps)
{
  if (corps == "AT"){list_neg = c(793, 794, 795, 796)}
  if (corps == "AA"){list_neg = c(791, 792, 0014, 0162)}
  if (corps == "AS"){list_neg = c(839 ,840, 841)}
  return(list_neg)
}

#### I. WOD ####

data_wod <- function(data, list_neg) 
{
  # Remove duplicates (why not in select_table?)
  di = data[data$annee == 2015,]
  dup = di$ident[duplicated(di$ident)]
  nb_indiv_bef_supp_dup <- (length(unique(data$ident)))
  data = data[which(!is.element(data$ident, dup)), ]
  nb_indiv_aft_supp_dup <- (length(unique(data$ident)))
  
  # Get number of individual for which we delete obs due to duplicates
  print(nb_indiv_bef_supp_dup - nb_indiv_aft_supp_dup)
  
  # Change types
  data$libemploi = as.character(data$libemploi)
  data$c_neg = as.numeric(format(data$c_neg))
  
  # Replace NA by 0 in c_neg
  data$c_neg[which(is.na(data$c_neg))] <- 0
  
  # Create annual var for echelon, using 4th trimestre
  data$echelon = data$echelon4
  
  # First/last ?????
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
  
  ## Correction: si grade[n-1] = grade[n+1] et != grade[n] on modifie grade[n] RAJOUTER IF ETAT == ACTIVITE
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
  data$missing_ech = ifelse(is.na(data$echelon) & data$libemploi != '', 1, 0) # Check meaning
  data$count_missing_ech = ave(data$missing_ech, data$ident, FUN = sum)
  
  return(data)
}

data_clean <- function(data, list_neg)
{
  list1 = data$ident[which(data$etat_4 == 1 & data$libemploi == '')]
  list2 = data$ident[which(data$c_neg == 0 & data$libemploi != '')]
  list3 = data$ident[which(is.na(data$echelon4) & is.element(data$c_neg, list_neg))]
  list = unique(union(union(list1,list2), list3))
  data_cleaned = data[which(!is.element(data$ident, list)),]  
  return(data_cleaned)
}

# Data
main_AT <- maintAT[order(mainAT[,2], mainAT[,4]), ]

data_all_AT   <- data_wod(data = mainAT, list_neg = list_neg_AT)
data_clean_AT <- data_clean(data_all_AT, list_neg_AT)

# data_all_AA   <- data_wod(data = mainAA, list_neg = list_neg_AA)
# data_clean_AA <- data_clean(data_all_AA, list_neg_AA)

rm(mainAT) #mainAA)
gc()

#### II. Data analysis ####

#### II.1 Sample selection ####

data_all = data_all_AT
list_neg = list_neg_AT
corps = 'AT'

sample_selection <- function(data, list_neg, corps)
{  
  list1 = data_all$ident[which(data_all$etat4 == 1 & data_all$libemploi == '')]
  list2 = data_all$ident[which(data_all$c_neg == 0 & data_all$libemploi != '')]
  list3 = data_all$ident[which(is.na(data_all$echelon) & is.element(data_all$c_neg, list_neg))]
  list4 = data_all$ident[which(is.element(data_all$c_neg, list_neg) & 
                                 data_all$c_neg == data_all$next_neg & 
                                 !is.na(data_all$echelon) & !is.na(data_all$next_ech) & 
                                 data_all$echelon>0 & data_all$next_ech>0 & 
                                 data_all$echelon>data_all$next_ech)]
  list5 = data_all$ident[which(is.element(data_all$c_neg, list_neg) & 
                                 data_all$c_neg == data_all$next_neg & 
                                 !is.na(data_all$echelon) & !is.na(data_all$next_ech) & 
                                 data_all$echelon>0 & data_all$next_ech>0 & 
                                 data_all$next_ech-data_all$echelon > 1)]
  
  size_sample = matrix(ncol = 2, nrow = 6)
  
  for (d in 1:6)
  {
    if (d == 1){dataset = data_all}
    if (d == 2){dataset = dataset[-which(is.element(dataset$ident, list1)),]}
    if (d == 3){dataset = dataset[-which(is.element(dataset$ident, list2)),]}
    if (d == 4){dataset = dataset[-which(is.element(dataset$ident, list3)),]}
    if (d == 5){dataset = dataset[-which(is.element(dataset$ident, list4)),]}
    if (d == 6){dataset = dataset[-which(is.element(dataset$ident, list5)),]}
    #size_sample[d,1] = length(dataset$ident)
    #size_sample[d,2] = 100*length(dataset$ident)/size_sample[1,1]
    size_sample[d,1] = length(unique(dataset$ident))
    size_sample[d,2] = 100*length(unique(dataset$ident))/size_sample[1,1]
  }
  
  colnames(size_sample) <- c("Nb d'individus", "\\% echantillon initial")
  rownames(size_sample) <- c("Echantillon initial",
                             "F1: Libemploi manquant quand etat4 est en activite",
                             "F2: Neg manquant quand libemploi renseigne", 
                             "F3: Echelon manquant quand neg dans le corps",
                             "F3bis: Baisse d'echelon", 
                             "F3ter: Saut d'echelon")
  
  print(xtable(size_sample,align="l|cc",nrow = nrow(size_sample), ncol=ncol(size_sample)+1, byrow=T, digits=0),
        hline.after=c(1), sanitize.text.function=identity,
        size="\\footnotesize", only.contents=T,
        file=paste0(tab_path, corps, "_sample_selection.tex"),)
  
}

sample_selection(data_all_AT, list_neg_AT, 'AT')


# II. 2. Dispersion duration échelon

# Add durée légale dans l'échelon en matchant les données admin et les grilles




# II. 3. Unicité de la trajectoire échelon-grade à échelon-grade ?
