######################################################################################################################## 
############################## TRAJECTORIES in ADJOINT TECHNIQUE CORPS 2011 -2015 ######################################
######################################################################################################################## 


#### 0. Initialisation ####

data_path = "M:/CNRACL/output/"
git_path =  'C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique'

tab_path = paste0(git_path,"ecrits/note_1_Lisa/Tables/")
grille_path = paste0(git_path, "")

#savepath = 'C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/ecrits/note_1_Lisa/Tables/'

### Loading packages and functions ###
source(paste0(git_path, '/modelisation/OutilsCNRACL.R'))

# Read csv
mainAT = read.csv(paste0(data_path,"corpsAT_2011_w_c_cir.csv"))
list_cir_AT = c('TTH1',
                'TTH2',
                'TTH3',
                'TTH4')
                

#### I. WOD ####

data_wod <- function(data, list_cir_AT) 
{
  # Remove duplicates (why not in select_table?)
  di = data[data$annee == 2015,]
  dup = di$ident[duplicated(di$ident)]
  nb_indiv_bef_supp_dup <- (length(unique(data$ident)))
  data = data[which(!is.element(data$ident, dup)), ]
  nb_indiv_aft_supp_dup <- (length(unique(data$ident)))
  
  # Get number of individual for which we delete obs due to duplicates
  print(nb_indiv_bef_supp_dup - nb_indiv_aft_supp_dup)
  stop
  # Change types
  data$libemploi = as.character(data$libemploi)
  data$c_cir = as.character(format(data$c_cir))
  
  # Replace NA by 0 in c_cir
  data$c_cir[which(is.na(data$c_cir))] <- '0'
  
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
  data$ind_AT = ifelse(is.element(data$c_cir, list_cir_AT), 1, 0)
  data$a = ave(data$ind_AT,data$ident,FUN=cumsum)
  data$first_AT <- ifelse(data$a==1,1,0)
  data$count_AT <-  ave(data$ind_AT, data$ident, FUN = sum)
  
  ## Correction: si grade[n-1] = grade[n+1] et != grade[n] on modifie grade[n] RAJOUTER IF ETAT == ACTIVITE
  data$bef_neg  <-ave(data$c_cir, data$ident, FUN=shiftm1)
  data = slide(data, "libemploi", GroupVar = "ident", NewVar = "bef_lib", slideBy = -1,
               keepInvalid = FALSE, reminder = TRUE)
  data = slide(data, "libemploi", GroupVar = "ident", NewVar = "bef_lib2", slideBy = -2,
               keepInvalid = FALSE, reminder = TRUE)
  data$next_cir <-ave(data$c_cir, data$ident, FUN=shift1)
  return(data$c_cir)
}
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

data_clean <- function(data, list_cir_AT)
{
  list1 = data$ident[which(data$etat_4 == 1 & data$libemploi == '')]
  list2 = data$ident[which(data$c_cir == 0 & data$libemploi != '')]
  list3 = data$ident[which(is.na(data$echelon4) & is.element(data$c_cir, list_cir_AT))]
  list = unique(union(union(list1,list2), list3))
  data_cleaned = data[which(!is.element(data$ident, list)),]  
  return(data_cleaned)
}

# Data
mainAT <- mainAT[order(mainAT[,2], mainAT[,4]), ]
data_all_AT   <- data_wod(data = mainAT, list_cir_AT = list_cir_AT)
data_clean_AT <- data_clean(data_all_AT, list_cir_AT)