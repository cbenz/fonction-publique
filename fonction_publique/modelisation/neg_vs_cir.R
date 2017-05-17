###### Comparison CIR vs NEG ####
# Difference between the two grade variables. 
# - Impact of filters
# - Transitions


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


# Data
data_neg = read.csv(paste0(data_path,"corpsAT_2011.csv"))
data_cir = read.csv(paste0(data_path,"corpsAT_2011_w_c_cir.csv"))


# # Code grade to numeric
# data_neg$grade = as.numeric(data_neg$c_neg)
# 
# data_cir$grade = data_cir$c_cir
# for (i in 0:9)
# {
# sub = as.character(i)  
# rep = LETTERS[i+1]
# data_cir$grade  = gsub(sub,rep, data_cir$grade)
# }  
# data_cir$grade = strtoi(data_cir$grade, 16L)
# 
# 
# list_neg = c("0793", "0794", "0795", "0796")
# list_cir = c("TTH1", "TTH2", "TTH3", "TTH4")


# Nombre de grade unique
length(unique(data_neg$c_neg))
length(unique(data_cir$c_cir))

# Nombre MV
length(which(data_neg$c_neg == ""))/length(data_neg$c_neg)
length(which(data_cir$c_cir == ""))/length(data_cir$c_cir)

# Nombre d'obs dans le corps
length(which(is.element(data_neg$c_neg, list_neg)))/length(data_neg$c_neg)
length(which(is.element(data_cir$c_cir, list_cir)))/length(data_cir$c_cir)



### I. Effect on filters  ####

sample_selection <- function(data, list_grade, var_grade)
{  
data$grade = data[,var_grade]  
  
list1 = data$ident[which(data$statut != "" & data$libemploi == ''  & data$annee>= 2011)]
list2 = data$ident[which(data$grade == "" & data$libemploi != '' & data$annee>= 2011)]
list3 = data$ident[which(is.na(data$echelon4) & is.element(data$grade, list_grade)  & data$annee>= 2011)]


size_sample = matrix(ncol = 2, nrow = 4)

for (d in 1:4)
{
  if (d == 1){dataset = data}
  if (d == 2){dataset = dataset[-which(is.element(dataset$ident, list1)),]}
  if (d == 3){dataset = dataset[-which(is.element(dataset$ident, list2)),]}
  if (d == 4){dataset = dataset[-which(is.element(dataset$ident, list3)),]}
  #size_sample[d,1] = length(dataset$ident)
  #size_sample[d,2] = 100*length(dataset$ident)/size_sample[1,1]
  size_sample[d,1] = length(unique(dataset$ident))
  size_sample[d,2] = 100*length(unique(dataset$ident))/size_sample[1,1]
}
  
return(size_sample)

}

selection_neg = sample_selection(data  = data_neg, list_grade =list_neg, var_grade = "c_neg")
selection_cir =  sample_selection(data = data_cir, list_cir, "c_cir")


### II. Effect on transition ####

shift1<-function(x){
  stopifnot(is.numeric(x))
  out<-NULL
  abs_shift_by=1
  out<-c(tail(x,-abs_shift_by),rep(NA,abs_shift_by))
  out
}

shiftm1<- function(x)  
{
  out <- shift(x,-1)
  return(out)
}

compute_transitions_entry <- function(data_all, list_grade, var_grade)
{
  data_all$grade = data_all[, var_grade]
  data_all$grade = strtoi(data_all$grade, base = 16L)
  list_grade= strtoi(list_grade, base = 16L)
  data_all$bef_grade <-ave(data_all$grade, data_all$ident, FUN=lag1)
  data_all$change_grade_bef  <- ifelse(data_all$grade == data_all$bef_grade , 0, 1)
  
  list1 = data_all$ident[which(data_all$statut != '' & data_all$libemploi == '')]
  list2 = data_all$ident[which(data_all$grade == "" & data_all$libemploi != '')]
  data_clean =  data_all[which(!is.element(data_all$ident, union(list1,list2))),]  
  data_entry = data_clean[which(data_clean$change_grade_bef ==1  & data_clean$annee >= 2012),]
  table_entry = matrix(0, ncol = length(list_grade), nrow = 11)  
  
  for (n in 1:length(list_grade))
  {
    list = which(data_entry$g == list_grade[n]) 
    # Intra-corps transitions
    for (n2 in 1:length(list_grade))
    {
      list2 = which(data_entry$change_grade_bef == list_grade[n2])
      table_entry[(n2),n] = length(intersect(list, list2))/length(list)  
    }
    # From other known neg
    list_oth = which(!is.element(data_entry$change_grade_bef, cbind(0, list_grade)))
    t = as.data.frame(table(data_entry$change_grade_bef[intersect(list, list_oth)]))
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
    list4 = which(data_entry$bef_grade == 0)
    table_entry[10,n] = length(intersect(list, list4))/length(list)  
    # Total: 
    table_entry[11, n] = sum(table_entry[-c(6:9,11), n])
  }
  table_entry[-c(6,8),] = table_entry[-c(6,8),]*100
  
  return(table_entry)
  
}  

compute_transitions_exit <- function(data_all, list_grade, var_grade)
{
  data_all$grade = data_all[, var_grade]
  
  data_all$grade = strtoi(data_all$grade, base = 8L)
  list_grade= strtoi(list_grade, base = 16L)
  
  data_all$next_grade   <-ave(data_all$grade, data_all$ident, FUN=lagm1)
  data_all$change_grade_next  <- ifelse(data_all$grade == data_all$next_grade , 0, 1)

  list1 = data_all$ident[which(data_all$statut != '' & data_all$libemploi == '')]
  list2 = data_all$ident[which(data_all$c_grade == 0 & data_all$libemploi != '')]
  data_clean =  data_all[which(!is.element(data_all$ident, union(list1,list2))),]  
  data_exit = data_clean[which(data_clean$change_grade_next ==1  & data_clean$annee >= 2011 & data_clean$annee < 2015),]
  table_exit = matrix(0, ncol = length(list_grade), nrow = 11)  
  
  for (n in 1:length(list_grade))
  {
    list = which(data_exit$grade == list_grade[n]) 
    # Intra-corps transitions
    for (n2 in 1:length(list_grade))
    {
      list2 = which(data_exit$next_grade == list_grade[n2])
      table_exit[(n2),n] = length(intersect(list, list2))/length(list)  
    }
    # From other known neg
    list_oth = which(!is.element(data_exit$next_grade, cbind(0, list_grade)))
    t = as.data.frame(table(data_exit$next_grade[intersect(list, list_oth)]))
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
    list4 = which(data_exit$next_grade == "0")
    table_exit[10,n] = length(intersect(list, list4))/length(list)  
    # Total: 
    table_exit[11, n] = sum(table_exit[1:10, n])
    table_exit[11, n] = sum(table_exit[-c(6:9,11), n])
  }
  table_exit[-c(6,8),] = table_exit[-c(6,8),]*100
  
  return(table_exit)
  
} 

exit_neg = compute_transitions_exit(data_all  = data_neg, list_grade =list_neg, var_grade = "c_neg")
exit_cir = compute_transitions_exit(data_all  = data_cir, list_grade =list_cir, var_grade = "c_cir")

entry_neg = compute_transitions_entry(data_all  = data_neg, list_grade =list_neg, var_grade = "c_neg")
entry_cir = compute_transitions_entry(data_all  = data_cir, list_grade =list_cir, var_grade = "c_cir")



