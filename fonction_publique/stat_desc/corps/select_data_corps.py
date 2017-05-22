# -*- coding: utf-8 -*-





# Filters: individuals at least one time in the corps
from __future__ import division

import os
import pandas as pd
import matplotlib.pyplot as plt

asset_path_careers = 'M:/CNRACL/clean/'
save_path = 'M:/CNRACL/output'
asset_path_corres_grades_corps = "C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/assets/corresp_neg_netneh.csv"
fig_save_path = "C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/ecrits/note_corps_Lisa/Figures/"

datasets = ['1980_1999_carrieres.h5',
#           '1976_1979_carrieres.h5',
#           '1970_1975_carrieres.h5',
#           '1960_1965_carrieres.h5',
#           '1966_1969_carrieres.h5'
           ]

where = "(annee >= 2012) & (annee <= 2013)"

list_data = []
for dataset in datasets:
    path = os.path.join(asset_path_careers, dataset)
    data = pd.read_hdf(path, "c_neg", where= where)
    data['c_neg'] = data['c_neg'].astype(str)
    data_w_c_neg_available = data[~data['c_neg'].isin([''])]
    list_data.append(data_w_c_neg_available)
    
data_careers = pd.concat(list_data)
data_careers = data_careers.drop_duplicates()
data_careers['c_neg'] = data_careers['c_neg'].str.zfill(4)


# On doit maintenant ajouter une colonne indiquant le corps
corres_grades_corps = pd.read_csv(asset_path_corres_grades_corps,
                                  sep = ";")

corres_grades_corps = corres_grades_corps[['CodeEmploiGrade_neg',
                                           'CadredemploiNEG']]
corres_grades_corps['CodeEmploiGrade_neg'] = corres_grades_corps['CodeEmploiGrade_neg'].astype(str)

dict_corres_grades_corps = corres_grades_corps.set_index(
                            'CodeEmploiGrade_neg'
                                ).to_dict()['CadredemploiNEG']

data_careers['corps'] = data_careers['c_neg'].map(dict_corres_grades_corps)
data_careers = data_careers.sort('ident')

# On regarde le nombre d'agents par corps en 2012
data_careers_2012 = data_careers[data_careers['annee'] == 2012]
count_per_corps = pd.DataFrame(data_careers_2012['corps'].value_counts().reset_index())
count_per_corps = count_per_corps.rename(columns = {'index':'Label corps en 2012', 'corps':'Nombre agents'})
print count_per_corps.to_latex()
print count_per_corps['Nombre agents'].sum()


# Vérifie le nombre d'identifiants uniques en 2012
data_careers_2012 = data_careers[data_careers['annee'] == 2012]
print len(data_careers_2012.ident.unique())

# On regarde pourquoi les corps sont parfois en NaN
data_careers_corps_NAN = data_careers[data_careers['corps'].isnull()]
data_careers_corps_NAN.c_neg.unique()
data_careers_corps_NAN_2012 = data_careers_corps_NAN[data_careers_corps_NAN['annee'] == 2012]
print len(data_careers_corps_NAN_2012.ident.unique())
# Ces NaN sont dus aux grades S09886', 'N00466', 'S08733', 'S05490', 'S10067', 'S04395'

###### Attention, 67 identifiants ont plusieurs codes grades pour l'année 2012
data_careers_2012_count_obs_per_ident = data_careers_2012.ident.value_counts().reset_index()
data_careers_2012_count_obs_per_ident_appearing_more_than_once = data_careers_2012_count_obs_per_ident[data_careers_2012_count_obs_per_ident['ident'] != 1]
# On trouve 67 identifiants apparaissant plusieurs fois en 2012, ie ayant plusieurs code grade neg en 2012


# On supprime les identifiants qui n'apparaissent qu'une des deux années
data_careers = data_careers[data_careers.groupby('ident').ident.transform(len) == 2]
print len(data_careers.ident.unique())
print len(data_careers_2012.ident.unique()) - len(data_careers.ident.unique())

# On crée une colonne corps 2013 pour chaque obs en 2012
data_careers_2012 = data_careers[data_careers['annee'] == 2012]
data_careers_2012 = data_careers_2012.rename(columns = {'corps':'corps_2012', 'c_neg':'c_neg_2012'})

data_careers_2013 = data_careers[data_careers['annee'] == 2013]
data_careers_2013 = data_careers_2013.rename(columns = {'corps':'corps_2013', 'c_neg':'c_neg_2013'})

data_careers = data_careers_2012.merge(data_careers_2013, on = 'ident')

# GRAPHIQUE 1: part des transitions intra corps entre 2012 et 2013, 21 corps, 0.92 (agents d'ent et agents sociaux territoriaux)
# On créé un dataframe du nombre de transitions entre les corps de 2012 à 2013 (to matrix to do)
data_corps = data_careers[['corps_2012', 'corps_2013', 'ident']]
data_corps = data_corps.groupby(['corps_2012', 'corps_2013']).count().reset_index()
data_corps = data_corps.rename(columns = {'ident':'count_of_idents'})

# On crée une variable qui donne la part des transitions intra corps pour chaque corps
data_corps['total_number_of_transitions_from_corps_2012'] = data_corps['count_of_idents'].groupby(data_corps['corps_2012']).transform('sum')
data_corps['share_of_transition_to_this_corps_2013_fr_corps_2012'] = data_corps['count_of_idents'] / data_corps['total_number_of_transitions_from_corps_2012']


# On graph maintenant les probabilités de transitions au même corps entre 2012 et 2013 pour chaque corps
data_transitions_intra_corps = data_corps[data_corps['corps_2012'] == data_corps['corps_2013']]

plt.hist(pd.to_numeric(
        data_transitions_intra_corps['share_of_transition_to_this_corps_2013_fr_corps_2012']), histtype='bar', rwidth=0.8)
plt.savefig(os.path.join(fig_save_path, 'transitions_intra_corps_2012_2013.png'), bbox_inches='tight')
# Nombre d'ident représentés
data_transitions_intra_corps['count_of_idents'].sum()
# Part des idens représentés
data_transitions_intra_corps['count_of_idents'].sum() / data_corps['count_of_idents'].sum()

# GRAPHIQUE 2: part des transitions intra corps entre 2012 et 2013, pour les agents qui changent de grade enntre 2012 et 2013
data_careers_only_w_c_neg_change = data_careers[data_careers['c_neg_2012'] != data_careers['c_neg_2013']]
print len(data_careers_only_w_c_neg_change) # 91 189

data_corps_only_w_c_neg_change = data_careers_only_w_c_neg_change[['corps_2012', 'corps_2013', 'ident']]
data_corps_only_w_c_neg_change = data_corps_only_w_c_neg_change.groupby(['corps_2012', 'corps_2013']).count().reset_index()
data_corps_only_w_c_neg_change = data_corps_only_w_c_neg_change.rename(columns = {'ident':'count_of_idents'})

# On crée une variable qui donne la part des transitions intra corps pour chaque corps
data_corps_only_w_c_neg_change['total_number_of_transitions_from_corps_2012'] = data_corps_only_w_c_neg_change['count_of_idents'].groupby(data_corps_only_w_c_neg_change['corps_2012']).transform('sum')
data_corps_only_w_c_neg_change['share_of_transition_to_this_corps_2013_fr_corps_2012'] = data_corps_only_w_c_neg_change['count_of_idents'] / data_corps_only_w_c_neg_change['total_number_of_transitions_from_corps_2012']

# On graph maintenant les probabilités de transitions au même corps entre 2012 et 2013 pour chaque corps
data_transitions_intra_corps_only_w_c_neg_change = data_corps_only_w_c_neg_change[data_corps_only_w_c_neg_change['corps_2012'] == data_corps_only_w_c_neg_change['corps_2013']]

plt.hist(pd.to_numeric(
        data_transitions_intra_corps_only_w_c_neg_change['share_of_transition_to_this_corps_2013_fr_corps_2012']), histtype='bar', rwidth=0.8)
plt.savefig(os.path.join(fig_save_path, 'transitions_intra_corps_only_w_c_neg_change_2012_2013.png'), bbox_inches='tight')
# Nombre d'ident représentés
data_transitions_intra_corps['count_of_idents'].sum()
# Part des idens représentés
data_transitions_intra_corps['count_of_idents'].sum() / data_corps['count_of_idents'].sum()

## GRAPHIQUE 3: taille des corps en 2012
data_corps_2012 = pd.DataFrame(data_careers['corps_2012'].value_counts().reset_index())
data_corps_2012 = data_corps_2012.rename(columns = {'index':'Label corps en 2012', 'corps_2012':'Nombre agents'})
print data_corps_2012.to_latex()

