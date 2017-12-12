##  Paths ####
rm(list = ls()); gc()


user = "simrab"

if (user == "simrab")
{
wd =  'U:/Projets/CNRACL/fonction-publique/fonction_publique/estimation/'
data_path = "M:/CNRACL/output/"
save_model_path = "Q:/CNRACL/predictions/"
simul_path  = "M:/CNRACL/simulation/results/"
python_file_path = 'U:/Projets/CNRACL/fonction-publique/fonction_publique/estimation/'
git_path =  'XXX/IPP/CNRACL'
fig_path = "Q:/CNRACL/Note CNRACL/Figures/"
tab_path = "Q:/CNRACL/Note CNRACL/Figures/"
}

setwd(wd)


if (user == "temp")
{
  wd =  'C:/Users/s.rabate/Desktop/temp/estimation/'
  data_path = "C:/Users/s.rabate/Desktop/temp/data/"
  save_model_path = "C:/Users/s.rabate/Desktop/temp/predictions/"
  simul_path  = "C:/Users/s.rabate/Desktop/temp/simulation/results/"
  python_file_path = 'C:/Users/s.rabate/Desktop/temp/estimation/'
  git_path =  'XXX/IPP/CNRACL'
  fig_path = "C:/Users/s.rabate/Desktop/temp/Note CNRACL/Figures/"
  tab_path = "C:/Users/s.rabate/Desktop/temp/Note CNRACL/Figures/"
}

setwd(wd)