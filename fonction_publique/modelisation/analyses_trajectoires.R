######################################################################################################################## 
######################################## TRAJECTORIES in ADJOINT TECHNIQUE CORPS ######################################
######################################################################################################################## 


#### 0. Initialisation ####


# path
if (place == ipp){
data_path = "M:/CNRACL/output/"
git_path =  'U:/Projets/CNRACL/fonction-publique/fonction_publique/'
}
fig_path = 
tab_path  
  
  ### Loading packages and functions ###
source(paste0(git_path, 'modelisation/OutilsCNRACL.R'))



# Read csv
main = read.csv(paste0(data_path,"corpsAT.csv"))

ident = unique(main$ident)
sub = sample(ident, 1000)
sub_data = main[which(is.element(main$ident, sub)), ]

data = sub_data

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
data <- data[, !names(data) %in% c('a', 'b', 'c')]
# AT variables
data$ind_AT = ifelse(is.element(data$c_neg, list_neg), 1, 0) 
data$count_AT = ave(data$ind_AT, data$ident, FUN = sum)
# Changing grades variable
data$bef_neg <-ave(data$c_neg, data$ident, FUN=shiftm1)
data$next_neg <-ave(data$c_neg, data$ident, FUN=shift1)
data$change_neg_bef  <- ifelse(data$c_neg == data$lag_neg, 0, 1)
data$change_neg_next <- ifelse(data$c_neg == data$next_neg, 0, 1)
# Ind libemploi 
data$ind_lib = ifelse(data$libemploi == '', 0, 1)
data$lag_ind_lib <-ave(data$ind_lib, data$ident, FUN=shiftm1)


#### II. General statistics on the AT population ####

#### II.1 Distribution of previous and next neg ####
list_neg = c(793, 794, 795, 796)
table_entry = matrix(ncol = length(list_neg), nrow = 9)
table_exit  = matrix(ncol = length(list_neg), nrow = 9)


data$bef <- data$bef_neg 
data$bef[which(data$bef == 0 & data$lag_ind_lib == 1)] = 999
data$bef[which(data$bef == 0 & data$lag_ind_lib == 0)] = 888


for (n in 1:length(list_neg))
{
list = which(data$c_neg == list_neg[n] & data$change_neg==1 & data$annne>2007) 
table[1,n] = length(list)
# From no lib
list1 = which(data$lag_ind_lib == 0)
table[2,n] = length(intersect(list, list1))/length(list)  
# From AT neg
  for (n2 in 1:length(list_neg))
  {
  list2 = which(data$lag_neg == list_neg[n2])
  table[(2+n2),n] = length(intersect(list, list2))/length(list)  
  }
# From other neg
list3 = which(!is.element(data$lag_neg,cbind(0,list_neg)))
table[7,n] = length(intersect(list, list3))/length(list)  
# From missing neg
list4 =  which(data$lag_neg == 0 & data$lag_ind_lib ==1)
table[8,n] = length(intersect(list, list4))/length(list)  
# Total: 
table[9,n] = sum(table[2:8,n])
}

colnames(table) <- c("AT2", "AT1", "ATP2", "ATP1")
rownames(table) <- c("Nb obs", "Libellé n-1 manquant", "NEG n-1 = AT2", "NEG n-1 = AT1", "NEG n-1 = ATP2", "NEG n-1 = ATP1",
                    "NEG n-1 = autres", "NEG n-1 = manquant", "total")
table<-desc
print(xtable(table,align="l|cccc",nrow = nrow(table), ncol=ncol(table)+1, byrow=T),
      hline.after=c(0,1,9), sanitize.text.function=identity,size="\\footnotesize", only.contents=T)


#### II.2 Distribution of destination ####




#### II.3 Distribution of destination when eligible ####

