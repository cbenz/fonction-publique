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

load_data <- function(data_path, corps)
{
  print(paste0("Loading data  ",corps))  
  filename = paste0(data_path,"corps",corps,"_2007.csv")
  main = read.csv(filename)  
  return (main)
}

get_list_neg <- function(corps)
{
  if (corps == "AT"){list_neg = c(793, 794, 795, 796)}
  if (corps == "AA"){list_neg = c(791, 792, 0014, 0162)}
  if (corps == "AS"){list_neg = c(839 ,840, 841, 773)}
  return(list_neg)
}  


#### I. WOD ####

data_wod <- function(data, list_neg, corps) 
{
  print(paste0("Cleaning data  ",corps)) 
  # Remove duplicates (why not in select_data.py?)
  di = data[data$annee == 2015,]
  dup = di$ident[duplicated(di$ident)]
  data = data[which(!is.element(data$ident, dup)), ]
  
  data$libemploi = as.character(data$libemploi)
  data$c_neg = as.numeric(format(data$c_neg))
  data$c_neg[which(is.na(data$c_neg))] <- 0
  data$echelon = data$echelon4
  data$etat = data$etat4
  # First/last
  data$a     <- 1
  data$b     <- ave(data$a,data$ident,FUN=cumsum)
  data$c     <- ave(data$a,data$ident,FUN=sum)
  data$first <- ifelse(data$b==1,1,0)
  data$last  <- ifelse(data$b==data$c,1,0)
  data$count = data$b
  data <- data[, !names(data) %in% c('a', 'b', 'c')]
  
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


#### II. Data analysis ####

#### II.1 Sample selection ####

sample_selection <- function(data_all, list_neg, corps, savepath)
{  
  list1 = data_all$ident[which(data_all$statut != "" & data_all$libemploi == ''  & data_all$annee>= 2007)]
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
                             "F1: Libemploi manquant quand statut non vide",
                             "F2: Neg manquant quand libemploi renseigne", 
                             "F3: Echelon manquant quand neg dans le corps",
                             "F3bis: Baisse d'echelon", 
                             "F3ter: Saut d'echelon")
  
  print(xtable(size_sample,align="l|cc",nrow = nrow(size_sample), ncol=ncol(size_sample)+1, byrow=T, digits=0),
        hline.after=c(1), sanitize.text.function=identity,
        size="\\footnotesize", only.contents=T,
        file=paste0(savepath, corps, "_sample_selection.tex"),)
  
}


# Nb d'observation par corps avant et après filtre
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





#### II.2 Data quality  ####

### II.2.1 proportion des missing echelon par annee ###


quality1 <- function(data, corps, list_neg, savepath)
{
  years = 2007:2015
  missing = matrix(ncol = 7, nrow = length(years))
  for (y in 1:length(years))
  {
    data1 = data[which(data$annee == years[y]), ]
    missing[y,1] =  length(which(data1$statut != '' & data1$libemploi == ''))/length(which(data1$statut != ''))
    missing[y,2] =  length(which(data1$c_neg == 0 & data1$libemploi != ''))/length(which(data1$libemploi != ''))
    missing[y,3] =  length(which(is.na(data1$echelon4) & data1$c_neg != 0))/length(which(data1$c_neg != 0))  
    missing[y,4] =  length(which(is.na(data1$echelon4) & data1$c_neg == list_neg[1]))/length(which(data1$c_neg == list_neg[1]))  
    missing[y,5] =  length(which(is.na(data1$echelon4) & data1$c_neg == list_neg[2]))/length(which(data1$c_neg == list_neg[2]))  
    missing[y,6] =  length(which(is.na(data1$echelon4) & data1$c_neg == list_neg[3]))/length(which(data1$c_neg == list_neg[3]))  
    missing[y,7] =  length(which(is.na(data1$echelon4) & data1$c_neg == list_neg[4]))/length(which(data1$c_neg == list_neg[4]))  
  }
  
  colnames(missing) <- c("\\% libemploi NA (statut OK)", "\\% neg NA (libemploi OK) ", "\\% ech NA", 
                         paste0("\\% ech NA ", list_neg))
  rownames(missing) <- years
  table = missing
  print(xtable(table,align="l|ccccccc",nrow = nrow(table), ncol=ncol(table)+1, byrow=T),
        sanitize.text.function=identity,size="\\footnotesize", 
        only.contents=T, include.colnames = F, hline.after = c(-1),
        file = paste0(savepath, corps, "_data_quality1.tex"))
  print(paste0("Saving table ",paste0(corps, "_data_quality1.tex")))
}



### II.2.2 Proportion des changements de grade par annee ###

quality2 <- function(data_all, corps,  list_neg, savepath)
{
  list1 = data_all$ident[which(data_all$statut != "" & data_all$libemploi == ''  & data_all$annee>= 2007)]
  list2 = data_all$ident[which(data_all$c_neg == 0 & data_all$libemploi != '' & data_all$annee>= 2007)]
  list3 = data_all$ident[which(is.na(data_all$echelon) & is.element(data_all$c_neg, list_neg)  & data_all$annee>= 2007)]
  
  years = 2008:2015
  evo1 = matrix(ncol = length(years), nrow = 4)
  evo2 = matrix(ncol = length(years), nrow = 4)
  evo3 = matrix(ncol = length(years), nrow = 4)
  
  for (y in 1:length(years))
  {
    data = data_all[which(data_all$annee == years[y]), ]
    data1 = data[-which(is.element(data$ident, list1)),]
    denom = length(data1$change_neg_bef) 
    evo1[1, y] = length(which(data1$change_neg_bef == 1))/denom
    evo1[2, y] = length(which(data1$change_neg_bef == 1 & data1$bef_neg == 0))/denom
    evo1[3, y] = length(which(data1$change_neg_bef == 1 & data1$c_neg == 0))/denom
    evo1[4, y] = length(which(data1$change_neg_bef == 1 & data1$c_neg != 0 & data1$bef_neg  != 0))/denom
    data2 = data1[-which(is.element(data1$ident, list2)),]
    denom = length(data2$change_neg_bef) 
    evo2[1, y] = length(which(data2$change_neg_bef == 1))/denom
    evo2[2, y] = length(which(data2$change_neg_bef == 1 & data2$bef_neg == 0))/denom
    evo2[3, y] = length(which(data2$change_neg_bef == 1 & data2$c_neg == 0))/denom
    evo2[4, y] = length(which(data2$change_neg_bef == 1 & data2$c_neg != 0 & data2$bef_neg  != 0))/denom
    data3 = data2[-which(is.element(data2$ident, list3)),]
    denom = length(data3$change_neg_bef) 
    evo3[1, y] = length(which(data3$change_neg_bef == 1))/denom
    evo3[2, y] = length(which(data3$change_neg_bef == 1 & data3$bef_neg == 0))/denom
    evo3[3, y] = length(which(data3$change_neg_bef == 1 & data3$c_neg == 0))/denom
    evo3[4, y] = length(which(data3$change_neg_bef == 1 & data3$c_neg != 0 & data3$bef_neg  != 0))/denom
  }
  
  count = 0
  for (table in list(evo1, evo2, evo3))
  {
    count = count + 1  
    rownames(table) <- c("\\% Changement de grade", "\\%  de NA a grade",
                         "\\% de grade a NA", "\\%  de grade a grade")
    
    print(xtable(table,align="ccccccccc",nrow = nrow(table), ncol=ncol(table)+1, byrow=T),
          sanitize.text.function=identity,size="\\footnotesize", 
          only.contents=T, include.colnames = F, hline.after = c(1),
          file = paste0(savepath, corps, "_data_quality2_",count,".tex"))
    print(paste0("Saving table ",paste0(corps,"_data_quality2_",count,".tex")))
  }
  
}




### II.2.3 Repartition des erreurs entre individus ###


### II.2.4 Repartition de la censure ###

count_censoring <- function(data_clean, list_neg, savepath, corps)
{
  data <- data_clean[which(data_clean$annee >= 2007), ]
  data$bef_neg  <- ave(data$c_neg, data$ident, FUN=shiftm1)
  data$change_neg_bef  <- ifelse(data$c_neg == data$bef_neg , 0, 1)
  data$change_neg_bef[data$annee == 2007] = 1
  # Count change grade
  data$cumsum  <- ave(data$change_neg_bef,data$ident,FUN=cumsum)
  data$tot     <- ave(data$change_neg_bef,data$ident,FUN=sum)  
  data = data[, c('ident', 'annee', 'cumsum',"c_neg")]
  data$seq = paste(data$ident, data$cumsum, sep = "_")
  # Removing sequences of empty neg
  data = data[-which(data$c_neg == 0), ]
  # Count number of sequences: 
  first_year <- tapply(data$annee,  data$seq, FUN = min) 
  last_year <-  tapply(data$annee,  data$seq, FUN = max) 
  # Count
  count = matrix(ncol = 5, nrow = 2)
  denom = length(first_year)
  count[1,1] = length(which(first_year > 2007 & last_year < 2015))
  count[1,2] = length(which(first_year == 2007 & last_year < 2015))
  count[1,3] = length(which(first_year > 2007 & last_year == 2015))
  count[1,4] = length(which(first_year == 2007 & last_year == 2015))
  
  count[1,5] = length(first_year)
  count[2,] = 100*count[1,]/denom
  
  table = count
  colnames(table) <- c("Cas 1", "Cas 2", "Cas 3", "Cas 4", "Total")
  rownames(table) <- c("Nombre", "Pourcentage")
  
  print(xtable(table, digits = matrix(c(rep(0,(ncol(table)+1)),rep(2,(ncol(table)+1))),
                                      nrow = nrow(table), ncol=(ncol(table)+1), byrow=T)),
        sanitize.text.function=identity,size="\\footnotesize", 
        only.contents=T, hline = c(0), 
        file = paste0(savepath, corps, "_censure.tex"))
  print(paste0("Saving table ",paste0( corps, "_censure.tex")))
}

#### III. Statistiques descriptives ####

#### III.1 Trajectories ####

# Sous pop: toute la carriere dans le corps, pas de missing. 

plot_random_trajectories = function(data_clean, list_neg, savepath, corps, Destinie = F)
{
  list_drop1 = unique(data_clean$ident[which(!is.element(data_clean$c_neg, list_neg) & data_clean$annee > 2006)])
  list_drop2 = unique(data_clean$ident[which(data_clean$ib4 == 0 & data_clean$annee > 2006)])
  list_keep = data_clean$ident[which(data_clean$an_aff == 2007 & data_clean$c_neg == 793 & data_clean$annee == 2007)]
  sub_ident = setdiff(list_keep, union(list_drop1, list_drop2))
  
  sub = sample(sub_ident , 16)
  sub_data = data_clean[which(is.element(data_clean$ident, sub) & data_clean$annee > 2006),]
  
  # Ind change grade
  sub_data$bef_neg  <-ave(sub_data$c_neg, sub_data$ident, FUN=shiftm1)
  sub_data$change_neg_bef  <- ifelse(sub_data$c_neg == sub_data$bef_neg, 0, 1)
  sub_data$ib_change1 <- sub_data$change_neg_bef*sub_data$ib4
  # Ind change grille 
  sub_data$change_grille  <- ifelse(is.element(sub_data$annee, c(2006, 2008, 2014, 2015)), 1, 0)
  sub_data$ib_change2 <- sub_data$change_grille*sub_data$ib4
  
  
  data1 = sub_data[, c("ident", 'annee', "ib4")]; data1$indice = data1$ib4
  data2 = sub_data[, c("ident", 'annee', "ib_change1")]; data2$indice = data2$ib_change1
  data3 = sub_data[, c("ident", 'annee', "ib_change2")]; data3$indice = data3$ib_change2
  lim = range(data1$ib[data1$ib4>0])
  
  #print(data1[1:10,])
  pdf(paste0(savepath, corps, "_trajectoires.pdf"))
  ggplot(data = data1, aes(x = annee, y = indice)) + geom_line() + 
    geom_point(data=data3, shape = 22, fill = "blue")+
    geom_point(data=data2, shape = 21, fill = "red")+
    ylim(lim[1], lim[2]) + 
    theme(strip.background = element_blank(), strip.text = element_blank(), axis.text.x=element_blank()) + 
    facet_wrap(~ident,  ncol = 4)
  dev.off()
  
  print(paste0("Saving graph  ",corps,"_trajectoires.pdf"))
  
  if (Destinie == T)
  {
    load("/Users/simonrabate/Desktop/PENSIPP 0.1/Modele/Outils/OutilsBio/BiosDestinie2-Old.RData")
    #load  ( (paste0("U:/PENSIPP 0.1/Modele/Outils/OutilsBio/BiosDestinie2-old.RData"        )) ) 
    sub_ident = which(anaiss == 90 & salaire[, 120]>0 & salaire[, 121]>0 & salaire[, 122]>0 & salaire[, 124]>0& salaire[, 125] >0 &
                        salaire[, 126]>0 & salaire[, 127]>0 & salaire[, 128] >0 & salaire[, 129]>0)
    sub = sample(sub_ident , 4)
    sub_data = as.data.frame(salaire[sub,120:129])
    sub_data$ident = 1:nrow(sub_data)
    colnames(sub_data) = paste0("age_",seq(20,29,1)) 
    sub_data2 = reshape(sub_data, idvar = "ident", varying = list(1:10) , direction = "long", sep = "_",  v.names = "salaire", timevar = "age")
    lim = range(sub_data[sub_data2>2000])
    pdf(paste0(savepath,"trajectoires_D.pdf"))
    ggplot(data = sub_data2, aes(x = age, y = salaire)) + geom_line() + 
      ylim(lim[1], lim[2]) + 
      theme(strip.background = element_blank(), strip.text = element_blank(), axis.text.x=element_blank()) + 
      facet_wrap(~ident,  ncol = 4)
    dev.off()
  }
}


#### III.2 Grade of entry and exit #### 

compute_transitions_entry <- function(data_all, list_neg, corps, savepath)
{
  list1 = data_all$ident[which(data_all$statut != '' & data_all$libemploi == '')]
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


#### III.3 Survival analysis ####

### III.3.1  Grade survival rate by entry year ###


survival_in_grade = function(data_all, corps, list_neg, savepath)  
{  
  list1 = data_all$ident[which(data_all$c_neg == 0 & data_all$libemploi != '')]
  list2 = data_all$ident[which(data_all$statut != '' & data_all$libemploi == '')]
  
  list = unique((union(list1,list2)))
  data = data_all[which(!is.element(data_all$ident, list)),]
  
  years = 2009:2014
  surv_1     = matrix(nrow = length(years), ncol = length(years))
  surv_rel_1 = matrix(nrow = length(years), ncol = length(years))
  
  surv = array(dim = c(length(list_neg), length(years), ncol = length(years)))
  surv_rel = array(dim = c(length(list_neg), length(years), ncol = length(years)))
  
  for (n in 1:length(list_neg))
  {
    for (y in 1:length(years))
    {
      list_keep1 = unique(data$ident[which(data$change_neg_bef == 1  & data$c_neg == list_neg[n] & data$annee == years[y])])
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
    pdf(paste0(savepath,corps,"_survival_",list_neg[n],".pdf"))
    n_col <- colorRampPalette(c("black", "grey80"))(length(years)) 
    type = rep(c(1,2),5)
    layout(matrix(c(1, 2, 3), nrow=3,ncol=1, byrow=TRUE), heights=c(3, 3,1))
    par(mar=c(4.1,4.1,0.2,0.2))
    # Nb
    table = surv[n, ,]
    plot  (years,rep(NA,length(years)),ylim=c(min(table, na.rm = T),max(table, na.rm = T)),ylab="Nb d'individus",xlab="Annee")
    for (a in 1:length(years)){lines(years,table[a, ],col=n_col[a],lwd=3, lty = type[a])}
    # Freq
    table = surv_rel[n, ,]
    plot  (years,rep(NA,length(years)),ylim=c(min(table, na.rm = T),max(table, na.rm = T)),ylab="% d'individus",xlab="Annee")
    for (a in 1:length(years)){lines(years,table[a, ],col=n_col[a],lwd=3, lty = type[a])}
    par(mar=c(0,0,0,0),font=1.5)
    plot.new()
    legend("center",legend=years, title = "Annee d'entree dans le grade:",
           col=n_col,lty=type[1:length(years)],lwd=3,cex=1.3, ncol=4, bty = "n")
    dev.off()
    print(paste0("Saving figure  ",corps,"_survival_",list_neg[n],".pdf"))
  }
}

### III.3.2  Conditional distribution for grade ###

hazard_rates = function(data_all, corps, list_neg, savepath)  
{  
  list1 = data_all$ident[which(data_all$c_neg == 0 & data_all$libemploi != '')]
  list2 = data_all$ident[which(data_all$statut != '' & data_all$libemploi == '')]
  list = unique((union(list1,list2)))
  data = data_all[which(!is.element(data_all$ident, list)),]
  
  for (entry_year in c(2007, 2009, 2011))
  {
    years = c((entry_year+1):2015)
    state =     matrix(nrow = 4, ncol = length(years))
    state_rel = matrix(nrow = 4, ncol = length(years))
    
    list_keep1 = unique(data$ident[which(data$c_neg == list_neg[1] & data$annee == entry_year & data$an_aff == entry_year)]) 
    sub_data = data[which(is.element(data$ident, list_keep1) & data$annee >= entry_year), c("ident", "annee", "c_neg", "bef_neg", "echelon", "echelon4", "libemploi", "change_neg_bef", "change_neg_next")] 
    sub_data$bef_ech = ave(sub_data$echelon4, sub_data$ident, FUN=shiftm1)
    
    for (y in 1:length(years))
    {
      stayers =  sub_data$ident[which(sub_data$bef_neg == list_neg[1] & sub_data$annee == years[y])]
      sub_data  =  sub_data[which(is.element(sub_data$ident, stayers)), ]
      state[1, y] = length(which(sub_data$c_neg == list_neg[1]& sub_data$annee == years[y]))
      state[2, y] = length(which(sub_data$c_neg == list_neg[2]& sub_data$annee == years[y]))
      state[3, y] = length(which(!is.element(sub_data$c_neg, c(0, list_neg[1], list_neg[2])) & sub_data$annee == years[y] ))
      state[4, y] = length(which(sub_data$c_neg == 0 & sub_data$annee == years[y]))
      state_rel[, y] = state[, y]/length(stayers)
    }  
    
    
    pdf(paste0(savepath, corps, "_destination_",entry_year,".pdf"))
    n_col = c("black", "grey40", "grey60", "grey80") 
    layout(matrix(c(1, 2), nrow=2,ncol=1, byrow=TRUE), heights=c(5,1))
    par(mar=c(2,2.5,1,1))
    barplot(state_rel, names.arg = years, col = n_col,
            args.legend = list(x = "bottomright"))
    par(mar=c(0,0,0,0),font=1)
    plot.new()
    legend("center",legend=c("Meme NEG", "Sortie NEG suivant", "Sortie autre NEG", "Sortie NA"),
           fill= n_col, cex=1, ncol = 2, bty = "n")
    dev.off()
    print(paste0("Saving figure :  ", corps, "_destination_",entry_year,".pdf"))
  }  
  
}


#### III.4  Distribution of next grade by echelon ####

hazard_rates_by_ech <- function(data_all, corps, list_neg, savepath)
{
  list1 = data_all$ident[which(data_all$statut != '' & data_all$libemploi == '')]
  list2 = data_all$ident[which(data_all$c_neg == 0 & data_all$libemploi != '')]
  data_clean =  data_all[which(!is.element(data_all$ident, union(list1,list2))),]    
  
  for (g in 1:length(list_neg))
  {
    data = data_clean[which(data_clean$c_neg == list_neg[g] & 
                              data_clean$annee >= 2011 & data_clean$annee <= 2014),]
    
    len = length(unique(data$echelon4))
    distrib_next = matrix(ncol = 4, nrow = (len-1))
    count_next = matrix(ncol = 4, nrow = (len-1))
    
    data$ind_stay  = ifelse(data$next_neg == data$c_neg, 1, 0) 
    if (g<4) {data$ind_exit1 = ifelse(data$next_neg == list_neg[g+1], 1, 0)}
    if (g==4){data$ind_exit1 = 0}
    data$ind_exit2 = ifelse(data$next_neg == 0, 1, 0) 
    if (g<4) {list_oth =  c(0, list_neg[g], list_neg[g+1])}
    if (g==4){list_oth =  c(0, list_neg[g])}
    data$ind_exit3 = ifelse(!is.element(data$next_neg, list_oth), 1, 0) 
    
    distrib_next[,1] = aggregate(data$ind_stay, list(data$echelon4), FUN = mean, na.rm = F)$x
    distrib_next[1,1] = mean(data$ind_stay[which(is.na(data$echelon4))])
    distrib_next[,2] = aggregate(data$ind_exit1, list(data$echelon4), FUN = mean, na.rm = F)$x
    distrib_next[1,2] = mean(data$ind_exit1[which(is.na(data$echelon4))])
    distrib_next[,3] = aggregate(data$ind_exit2, list(data$echelon4), FUN = mean, na.rm = F)$x
    distrib_next[1,3] = mean(data$ind_exit2[which(is.na(data$echelon4))])
    distrib_next[,4] = aggregate(data$ind_exit3, list(data$echelon4), FUN = mean, na.rm = F)$x
    distrib_next[1,4] = mean(data$ind_exit3[which(is.na(data$echelon4))])
    
    count_next[,1] = aggregate(data$ind_stay, list(data$echelon4), FUN = sum, na.rm = F)$x
    count_next[1,1] = sum(data$ind_stay[which(is.na(data$echelon4))])
    count_next[,2] = aggregate(data$ind_exit1, list(data$echelon4), FUN = sum, na.rm = F)$x
    count_next[1,2] = sum(data$ind_exit1[which(is.na(data$echelon4))])
    count_next[,3] = aggregate(data$ind_exit2, list(data$echelon4), FUN = sum, na.rm = F)$x
    count_next[1,3] = sum(data$ind_exit2[which(is.na(data$echelon4))])
    count_next[,4] = aggregate(data$ind_exit3, list(data$echelon4), FUN = sum, na.rm = F)$x
    count_next[1,4] = sum(data$ind_exit3[which(is.na(data$echelon4))])
    
    t = table(data_clean[which(data_clean$c_neg == 794 & data_clean$change_neg_next == 1 & data_clean$echelon4 == 2 &
                                 data_clean$annee >= 2011 & data_clean$annee < 2015),"next_neg"])
    t / length(data_clean[which(data_clean$c_neg == 794 & data_clean$change_neg_next == 1 & data_clean$echelon4 == 2 & 
                                  data_clean$annee >= 2011 & data_clean$annee < 2015),"next_neg"])
    t = table(data_clean[which(data_clean$c_neg == 794 & data_clean$change_neg_next == 1 & data_clean$echelon4 == 4 &
                                 data_clean$annee >= 2011 & data_clean$annee < 2015),"next_neg"])
    t / length(data_clean[which(data_clean$c_neg == 794 & data_clean$change_neg_next == 1 & data_clean$echelon4 == 4 & 
                                  data_clean$annee >= 2011 & data_clean$annee < 2015),"next_neg"])
    # => 80% ces departs vers "autres grades" correspondent a des departs vers le AT2 => bizarre!
    
    n_col = c("black", "grey40", "grey60", "grey80") 
    
    pdf(paste0(fig_path,corps, "_hazard_by_ech_",list_neg[g],".pdf"))
    
    layout(matrix(c(1, 2, 3, 3), nrow=2,ncol=2, byrow=TRUE), heights=c(5,1))
    par(mar=c(4,3,1,1))
    barplot(t(count_next), col = n_col,
            xlab = "Echelon", ylab = "Count",
            names.arg = c("NA", seq(1,(len-2),1)), xpd = FALSE,
            args.legend = list(x = "bottomright"))
    barplot(t(distrib_next), col = n_col,
            xlab = "Echelon", ylab = "Frequency",
            names.arg = c("NA", seq(1,(len-2),1)), ylim = c(0.5, 1), xpd = FALSE,
            args.legend = list(x = "bottomright"))
    par(mar=c(0,0,0,0),font=1.5)
    plot.new()
    legend("center",legend=c("Grade courant", "Prochain grade", "Manquant", "Autre"), title = "Grade a l'annee suivante :",
           fill= n_col, cex=1.2, ncol = 4, bty = "n")
    
    dev.off()  
    
    print(paste0("Saving figure :  ",corps, "_hazard_by_ech_",list_neg[g],".pdf"))
    
  }
  
}


#### III.5 Distribution of time spent in grade and echelon ####

## III.5.1 Time spent in grade ##


## III.5.2 Time spent in echelon (filter: entering new echelon in 2012) ##

duration_in_ech <- function(data_clean, list_neg, savepath, corps)
{
  data =  data_clean[which(data_clean$annee >= 2011), c("ident", "annee", "c_neg",'bef_neg' , 'an_aff',
                                                        "echelon1", "echelon2", "echelon3", "echelon4")] 
  data = reshape(data, idvar = c("ident", "annee"), v.names = "ech", timevar = "trimestre",
                 varying = c("echelon1", "echelon2", "echelon3", "echelon4") , direction = "long")
  data = data[order(data$ident,data$annee,data$trimestre),]
  
  list = data$ident[which(is.na(data$ech))]
  data = data[which(!is.element(data$ident, list)),]
  
  # Change echelon
  data$bef_ech <-ave(data$ech, data$ident, FUN=shiftm1)
  data$change_ech <- ifelse((data$ech != data$bef_ech), 1, 0)
  data$change_ech[is.na(data$change_ech)] = 1
  data$cumsum  <- ave(data$change_ech,data$ident,FUN=cumsum)
  data$tot     <- ave(data$change_ech,data$ident,FUN=sum)
  
  # Pop: changement d'echelon entre 2011 et 2012: 
  list_keep = data$ident[which(data$annee == 2012 & data$cumsum == 2)]
  data2 = data[which(is.element(data$ident, list_keep)),]
  data2 = data2[which(data2$tot > 2 & data2$cumsum == 2), ]
  data2$a = 1
  data2$count = ave(data2$a, data2$ident, FUN=cumsum)
  data2$tot   = ave(data2$a, data2$ident, FUN=sum)
  datai = data2[which(data2$count == 1), ]
  
  table(datai$tot)
  par(mar=c(4,4,0.1,1))
  hist(datai$tot, 
       xlab="Duree (en trimestre)", ylab = "Frequence", main = "",
       col="grey50",
       border="black", 
       xlim=c(1,15))
  
  # Differenciation par neg et echelon
  list_keep = data$ident[which(data$annee == 2012 & data$cumsum == 2 & data$c_neg == list_neg[1])]
  data2 = data[which(is.element(data$ident, list_keep)),]
  data2 = data[which(data$tot > 2 & data$cumsum == 2), ]
  data2$a = 1
  data2$count = ave(data2$a, data2$ident, FUN=cumsum)
  data2$tot   = ave(data2$a, data2$ident, FUN=sum)
  datai = data2[which(data2$count == 1), ]
  
  
  pdf(paste0(fig_path,"duree_ech_AT2.pdf"))
  
  layout(matrix(c(1,2,3,4), nrow=2,ncol=2, byrow=TRUE), heights=c(3,3))
  
  par(mar=c(2,2,2,2))
  h = hist(datai$tot, 
           xlab="Duree (en trimestre)", ylab = "Frequence", main = "(a) Tous",
           col="grey50",xaxt="n",
           border="black", 
           xlim=c(1,15))
  axis(side=1,at=h$breaks[c(2,4,6,8,10,12,14,16)],labels=(h$breaks*3)[c(2,4,6,8,10,12,14,16)], font = 0.8)
  
  h =hist(datai$tot[which(datai$ech >= 2 & datai$ech < 4 )],  
          xaxt="n", ylab = "Frequence", main = "(b) Echelons 2 et 3",
          col="grey50",
          border="black", 
          xlim=c(1,15))
  axis(side=1,at=h$breaks[c(2,4,6,8,10,12,14,16)],labels=(h$breaks*3)[c(2,4,6,8,10,12,14,16)], font = 0.8)
  
  h =hist(datai$tot[which(datai$ech >= 4 & datai$ech < 7 )],  
          xaxt="n", ylab = "Frequence", main = "(c) Echelons 4, 5 et 6",
          col="grey50",
          border="black", 
          xlim=c(1,15))
  axis(side=1,at=h$breaks[c(2,4,6,8,10,12,14,16)],labels=(h$breaks*3)[c(2,4,6,8,10,12,14,16)], font = 0.8)
  
  h =hist(datai$tot[which(datai$ech >= 7 & datai$ech < 11 )],  
          xaxt="n", ylab = "Frequence", main = "(d) Echelons 7, 8, 9 et 10",
          col="grey50",
          border="black", 
          xlim=c(1,15))
  axis(side=1,at=h$breaks[c(2,4,6,8,10,12,14,16)],labels=(h$breaks*3)[c(2,4,6,8,10,12,14,16)], font = 0.8)
  
  dev.off()
  
}

##### MAIN #####

main <- function(liste_corps)
{
  for (corps in liste_corps)
  {
    # Load data
    main = load_data(data_path, corps)
    list_neg = get_list_neg(corps)
    data_all =  data_wod(data = main, list_neg = list_neg, corps = corps)
    data_clean = data_clean(data_all, list_neg)
    rm(main)
    gc()
    # Filters 
    sample_selection(data_all = data_all, corps = corps, list_neg = list_neg, savepath = tab_path)
    count1(data_all = data_all, corps = corps, list_neg = list_neg, savepath = tab_path)
    # Quality
    quality1(data = data_all, corps = corps, list_neg = list_neg, savepath = tab_path)
    quality2(data_all = data_all, corps = corps, list_neg = list_neg, savepath = tab_path)
    count_censoring(data_clean = data_clean, corps = corps, list_neg = list_neg, savepath = tab_path)
    # Trajectories
    if (corps == 'AT'){plot_random_trajectories(data_clean = data_clean, corps = corps, list_neg = list_neg, savepath = fig_path)}
    # Transitions
    compute_transitions_entry(data = data_all, corps = corps, list_neg = list_neg, savepath = tab_path)
    compute_transitions_exit(data = data_all, corps = corps, list_neg = list_neg, savepath = tab_path)
    # Survival by entry year
    survival_in_grade(data_all = data_all, corps = corps, list_neg = list_neg, savepath = fig_path)  
    # Hazard rates by entry year
    hazard_rates(data_all = data_all, corps = corps, list_neg = list_neg, savepath = fig_path)  
    # Hazard rates by echelon
    hazard_rates_by_ech(data_all = data_all, corps = corps, list_neg = list_neg, savepath = fig_path)    
  } 
}  

main('AT')
#main('AA')
#main('AS')