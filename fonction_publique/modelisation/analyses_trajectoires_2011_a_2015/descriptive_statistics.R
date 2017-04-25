######################################################################################################################## 
############################## TRAJECTORIES in ADJOINT TECHNIQUE CORPS 2011 -2015 ######################################
######################################################################################################################## 


#### 0. Initialisation ####

data_path = "M:/CNRACL/output/"
git_path =  'C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique'

tab_path = paste0(git_path,"ecrits/note_1_Lisa/Tables/")
grille_path = paste0(git_path, "")

savepath = 'C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/ecrits/note_1_Lisa/Tables/'

### Loading packages and functions ###
source(paste0(git_path, 'modelisation/OutilsCNRACL.R'))

# Read csv
mainAT = read.csv(paste0(data_path,"corpsAT_2011.csv"))
list_neg_AT = c(793, 794, 795, 796)
#sub_data_AT = mainAT[which(is.element(mainAT$ident, sample(unique(mainAT$ident), 10000))), ]

# mainAA = read.csv(paste0(data_path,"corpsAA_2011.csv"))
# list_neg_AA = c(791, 792, 0014, 0162)
# #sub_data_AA = mainAA[which(is.element(mainAA$ident, sample(unique(mainAA$ident), 10000))), ]
# 
# mainAS = read.csv(paste0(data_path,"corpsAS_2011.csv"))
# list_neg_AS = c(839 ,840, 841, 773)
#sub_data_AS = mainAS[which(is.element(mainAS$ident, sample(unique(mainAS$ident), 10000))), ]

# Read CSV debug
debugAT = read.csv(paste0(data_path,"/debug/corpsAT_2007.csv"))

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
  stop
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
mainAT <- mainAT[order(mainAT[,2], mainAT[,4]), ]
data_all_AT   <- data_wod(data = mainAT, list_neg = list_neg_AT)
data_clean_AT <- data_clean(data_all_AT, list_neg_AT)

# mainAA <- mainAA[order(mainAA[,2], mainAA[,4]), ]
# data_all_AA   <- data_wod(data = mainAA, list_neg = list_neg_AA)
# data_clean_AA <- data_clean(data_all_AA, list_neg_AA)
# 
# mainAS <- mainAS[order(mainAS[,2], mainAS[,4]), ]
# data_all_AS   <- data_wod(data = mainAS, list_neg = list_neg_AS)
# data_clean_AS <- data_clean(data_all_AS, list_neg_AS)


rm(mainAT, mainAA, mainAS)
gc()

#### II. Data analysis ####

#### II.1 Sample selection ####

data_all = data_all_AT
list_neg = list_neg_AT
corps = 'AT'

sample_selection <- function(data_all, list_neg, corps, savepath)
{  
  list1 = data_all$ident[which(data_all$etat4 == 1 & data_all$libemploi == ''  & data_all$annee>= 2007)]
  list2 = data_all$ident[which(data_all$c_neg == 0 & data_all$libemploi != '' & data_all$annee>= 2007)]
  list3 = data_all$ident[which(is.na(data_all$echelon) & is.element(data_all$c_neg, list_neg)  & data_all$annee>= 2007)]
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
                             "F1: Libemploi manquant quand etat activite",
                             "F2: Neg manquant quand libemploi renseigne", 
                             "F3: Echelon manquant quand neg dans le corps",
                             "F3bis: Baisse d'echelon", 
                             "F3ter: Saut d'echelon")
  
  print(xtable(size_sample,align="l|cc",nrow = nrow(size_sample), ncol=ncol(size_sample)+1, byrow=T, digits=0),
        hline.after=c(1), sanitize.text.function=identity,
        size="\\footnotesize", only.contents=T,
        file=paste0(savepath, corps, "_sample_selection.tex"),)
  
}

sample_selection(data_all_AT, list_neg_AT, 'AT', savepath)
sample_selection(data_all_AA, list_neg_AA, 'AA', savepath)
sample_selection(data_all_AS, list_neg_AS, 'AS', savepath)

#count
count1 <- function(data_all, corps, list_neg, savepath)
{
  list1 = data_all$ident[which(data_all$statut != "" & data_all$libemploi == ''  & data_all$annee>= 2007)]
  list2 = data_all$ident[which(data_all$c_neg == 0 & data_all$libemploi != '' & data_all$annee>= 2007)]
  list3 = data_all$ident[which(is.na(data_all$echelon) & is.element(data_all$c_neg, list_neg)  & data_all$annee>= 2007)]  
  data1 =  data_all[-which(is.element(data_all$ident, list1)),]
  data2 =  data1[-which(is.element(data1$ident, list2)),]
  data3 =  data2[-which(is.element(data2$ident, list3)),]
  
  count = matrix(ncol = length(list_neg)*2, nrow = 4)
  
  for (n in 1:length(list_neg))
  {
    count[1, (n*2 - 1)] =  length(which(data_all$c_neg == list_neg[n]))
    count[1, n*2]       =  100*length(which(data_all$c_neg == list_neg[n]))/  count[1, (n*2 - 1)]
    count[2, (n*2 - 1)] =  length(which(data1$c_neg == list_neg[n]))
    count[2, n*2]       =  100*length(which(data1$c_neg == list_neg[n]))/  count[1, (n*2 - 1)]
    count[3, (n*2 - 1)] =  length(which(data2$c_neg == list_neg[n]))
    count[3, n*2]       =  100*length(which(data2$c_neg == list_neg[n]))/  count[1, (n*2 - 1)]
    count[4, (n*2 - 1)] =  length(which(data3$c_neg == list_neg[n]))
    count[4, n*2]       =  100*length(which(data3$c_neg == list_neg[n]))/  count[1, (n*2 - 1)]
  }
  
  rownames(count) <- c("Tous","F1", "F2", "F3")
  table = count
  print(xtable(table,align="l|cccccccc",nrow = nrow(table), ncol=ncol(table)+1, byrow=T, digits = 0),
        sanitize.text.function=identity,size="\\footnotesize", 
        only.contents=T, include.colnames = F, hline.after = c(-1),
        file = paste0(savepath, corps, "_data_count1.tex"))
  print(paste0("Saving table ",paste0(corps, "_data_count1.tex")))
}

# II. Matrices de transitions
compute_transitions_entry <- function(data_all, list_neg, corps, savepath)
{
  list1 = data_all$ident[which(data_all$etat4 == 1 & data_all$libemploi == '')]
  list2 = data_all$ident[which(data_all$c_neg == 0 & data_all$libemploi != '')]
  data_clean =  data_all[which(!is.element(data_all$ident, union(list1,list2))),]  
  data_entry = data_clean[which(data_clean$change_neg_bef ==1  & data_clean$annee >= 2012),]
  table_entry = matrix(0, ncol = length(list_neg), nrow = 11)  
  
  for (n in 1:length(list_neg))
  {
    list = which(data_entry$c_neg == list_neg[n]) 
    # Intra-corps transitions
    for (n2 in 1:length(list_neg))
    {
      list2 = which(data_entry$bef_neg == list_neg[n2])
      table_entry[(n2),n] = length(intersect(list, list2))/length(list)  
    }
    # From other known neg
    list_oth = which(!is.element(data_entry$bef_neg, cbind(0, list_neg)))
    t = as.data.frame(table(data_entry$bef_neg[intersect(list, list_oth)]))
    t = t[order(-t$Freq),]
    if (length(intersect(list, list_oth))>0)
    {
      table_entry[5,n] = sum(t$Freq)/length(list)  
      table_entry[6,n] = as.numeric(format(t[1,1]))
      table_entry[7,n] = t[1,2]/length(list) 
      table_entry[8,n] = round(as.numeric(format(t[2,1])), digits = 0)
      table_entry[9,n] = t[2,2]/length(list) 
    }
    # From missing neg
    list4 = which(data_entry$bef_neg == 0)
    table_entry[10,n] = length(intersect(list, list4))/length(list)  
    # Total: 
    table_entry[11, n] = sum(table_entry[-c(6:9,11), n])
  }
  table_entry[-c(6,8),] = table_entry[-c(6,8),]*100
  table = table_entry
  print(list_neg)
  colnames(table) <- paste0("NEG n = ", list_neg)
  rownames(table) <- c(paste0("NEG n-1 = ", list_neg),
                       "NEG n-1 = autres", " \\hfill dont le grade ", "\\hfill  representant ", 
                       " \\hfill dont le grade ", "\\hfill  representant ",
                       "NEG n-1 = manquant", "total")
  
  print(xtable(data.frame(var  = rownames(table), data.frame(table)),
               digits = matrix(c(rep(2,(ncol(table)+2)*5),rep(0,(ncol(table)+2)*1), 
                                 rep(2,(ncol(table)+2)*1),rep(0,(ncol(table)+2)*1),
                                 rep(2,(ncol(table)+2)*3)),nrow = nrow(table), ncol=ncol(table)+2, byrow=T)),
        sanitize.text.function=identity,size="\\footnotesize", 
        only.contents=T, hline = c(4,9), include.rownames = FALSE, include.colnames = FALSE,
        file = paste0(savepath, corps, "_transition_entry.tex"))
  print(paste0("Saving figure ",paste0( corps, "_transition_entry.tex")))
}  

compute_transitions_entry(data_all_AT, list_neg_AT, 'AT', savepath)
compute_transitions_entry(data_all_AS, list_neg = list_neg_AS, corps = 'AS', savepath)
compute_transitions_entry(data_all_AA, list_neg_AA, 'AA', savepath)

compute_transitions_exit <- function(data_all, list_neg, corps, savepath = tab_path)
{
  list1 = data_all$ident[which(data_all$statut != '' & data_all$libemploi == '')]
  list2 = data_all$ident[which(data_all$c_neg == 0 & data_all$libemploi != '')]
  data_clean =  data_all[which(!is.element(data_all$ident, union(list1,list2))),]  
  data_exit = data_clean[which(data_clean$change_neg_next ==1  & data_clean$annee >= 2011 & data_clean$annee < 2015),]
  table_exit = matrix(0, ncol = length(list_neg), nrow = 11)  
  
  for (n in 1:length(list_neg))
  {
    list = which(data_exit$c_neg == list_neg[n]) 
    # Intra-corps transitions
    for (n2 in 1:length(list_neg))
    {
      list2 = which(data_exit$next_neg == list_neg[n2])
      table_exit[(n2),n] = length(intersect(list, list2))/length(list)  
    }
    # From other known neg
    list_oth = which(!is.element(data_exit$next_neg, cbind(0, list_neg)))
    t = as.data.frame(table(data_exit$next_neg[intersect(list, list_oth)]))
    t = t[order(-t$Freq),]
    if (length(intersect(list, list_oth))>0)
    {
      table_exit[5,n] = sum(t$Freq)/length(list)  
      table_exit[6,n] = as.numeric(format(t[1,1]))
      table_exit[7,n] = t[1,2]/length(list) 
      table_exit[8,n] = round(as.numeric(format(t[2,1])), digits = 0)
      table_exit[9,n] = t[2,2]/length(list)
    }
    # From missing neg
    list4 = which(data_exit$next_neg == 0)
    table_exit[10,n] = length(intersect(list, list4))/length(list)  
    # Total: 
    table_exit[11, n] = sum(table_exit[1:10, n])
    table_exit[11, n] = sum(table_exit[-c(6:9,11), n])
  }
  table_exit[-c(6,8),] = table_exit[-c(6,8),]*100
  
  table = table_exit
  colnames(table) <- paste0("NEG n = ", list_neg)
  rownames(table) <- c(paste0("NEG n+1 = ", list_neg),
                       "NEG n+1 = autres", " \\hfill dont le grade ", "\\hfill  representant ", 
                       " \\hfill dont le grade ", "\\hfill  representant ",
                       "NEG n+1 = manquant", "total")
  
  
  print(xtable(data.frame(var  = rownames(table), data.frame(table)),
               digits = matrix(c(rep(2,(ncol(table)+2)*5),rep(0,(ncol(table)+2)*1), 
                                 rep(2,(ncol(table)+2)*1),rep(0,(ncol(table)+2)*1),
                                 rep(2,(ncol(table)+2)*3)),nrow = nrow(table), ncol=ncol(table)+2, byrow=T)),
        sanitize.text.function=identity,size="\\footnotesize", 
        only.contents=T, hline = c(4,9), include.rownames = FALSE, include.colnames = FALSE,
        file = paste0(savepath, corps, "_transition_exit.tex"))
  print(paste0("Saving figure ",paste0( corps, "_transition_exit.tex")))
} 

compute_transitions_exit(data_all_AT, list_neg_AT, 'AT', savepath)
compute_transitions_exit(data_all_AS, list_neg = list_neg_AS, corps = 'AS', savepath)
compute_transitions_exit(data_all_AA, list_neg_AA, 'AA', savepath)

# II. 2. Dispersion duration échelon

mainAT_w_conditions <- read.csv(paste0(data_path,"corps_AT_2011_w_echelon_conditions.csv"))

mainAT_w_conditions$ident = as.character(mainAT_w_conditions$ident)
mainAT_w_conditions$c_neg = as.character(mainAT_w_conditions$c_neg)
mainAT_w_conditions$echelon_x = as.character(mainAT_w_conditions$echelon_x)
mainAT_w_conditions$ident_cneg_ech <- as.character(with(mainAT_w_conditions, paste0(ident, c_neg, echelon_x)))
mainAT_w_conditions$number_of_quarters_in_cneg_ech <- transform(mainAT_w_conditions, count = table(ident_cneg_ech)[ident_cneg_ech])

mainAT_w_conditions$number_of_months_in_cneg_ech <- as.numeric(as.character(mainAT_w_conditions$number_of_quarters_in_cneg_ech)) * 3
par(mfrow = c(3, 2))

list_unique_period_min <- unique(mainAT_w_conditions$min_mois)
for (n in 1:length(list_unique_period_min)){
  period_min = list_unique_period_min[n]
  data = mainAT_w_conditions[mainAT_w_conditions$min_mois == period_min,]
  hist(data$number_of_months_in_cneg_ech, main = "")
}
  
  
# II. 3. Unicité de la trajectoire échelon-grade à échelon-grade ?
