# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 09:40:08 2017

@author: l.degalle
"""

# Filters: individuals at least one time in the corps
from __future__ import division

import os
import pandas as pd
import matplotlib.pyplot as plt
from fonction_publique.base import asset_path, project_path, output_directory_path, clean_directory_path


fig_save_path = os.path.join(project_path, "/ecrits/note_corps_Lisa/Figures/")

datasets = [
            'pamplemousse.h5',
           '1976_1979_carrieres.h5',
           '1970_1975_carrieres.h5',
           '1960_1965_carrieres.h5',
           '1966_1969_carrieres.h5'
           ]

where = "(annee >= 2012) & (annee <= 2013)"

list_data = []
for dataset in datasets:
    path = os.path.join(asset_path_careers, dataset)
    data = pd.read_hdf(path, "c_cir", where= where)
    data['c_cir'] = data['c_cir'].astype(str)
    data_w_c_cir_available = data[~data['c_cir'].isin([''])]
    list_data.append(data_w_c_cir_available)
    
data_careers = pd.concat(list_data)
data_careers_2012 = data_careers[data_careers['annee'] == 2012]
print "Il y a {} agents dans les données en 2012".format(
    len(data_careers_2012.ident.unique())
    )
data_careers = data_careers.drop_duplicates()
data_careers['c_cir'] = data_careers['c_cir'].str.zfill(4)


# On doit maintenant ajouter une colonne indiquant le corps
corres_grades_corps = pd.read_csv( os.path.join(asset_path, "corresp_neg_netneh.csv"),
                                  sep = ";")

corres_grades_corps = corres_grades_corps[['CodeNETNEH_neg',
                                           'CadredemploiNEG']]
corres_grades_corps['CodeNETNEH_neg'] = corres_grades_corps[
        'CodeNETNEH_neg'
        ].astype(str)

dict_corres_grades_corps = corres_grades_corps.set_index(
                            'CodeNETNEH_neg'
                                ).to_dict()['CadredemploiNEG']

data_careers['corps'] = data_careers['c_cir'].map(dict_corres_grades_corps)
# 14 pourcents de missing corps dûs à des c_cir qu'on n'a pas dans la table de corres, emplois nationaux ? 
data_careers = data_careers.sort('ident')

# On regarde le nombre d'agents par corps en 2012
data_careers_2012 = data_careers[data_careers['annee'] == 2012]
count_per_corps = pd.DataFrame(
        data_careers_2012['corps'].value_counts().reset_index()
        )
count_per_corps = count_per_corps.rename(
        columns = {'index':'Label corps en 2012', 'corps':'Nombre agents'}
        )
count_per_corps['Part du total'] = count_per_corps[
        'Nombre agents'
        ] / len(data_careers_2012['ident'].unique())
pd.options.display.float_format = '{:.2%}'.format
count_per_corps['Part cumulee du total'] = count_per_corps[
        'Part du total'
        ].cumsum()
print count_per_corps.to_latex()
print "{} des agents qui ont un c_cir renseigné en 2012 sont représentés (soit {} agents), car {} n'ont pas pu être rattachés à un corps".format(count_per_corps['Part du total'].sum(), count_per_corps['Nombre agents'].sum(), 
      len(data_careers_2012[
              data_careers_2012['corps'].isnull()
              ]) / len(data_careers_2012))
print "{} corps sont représentés".format(
        len(count_per_corps['Label corps en 2012'].unique())
        )


# Vérifie le nombre d'identifiants uniques en 2012
data_careers_2012 = data_careers[data_careers['annee'] == 2012]
print "Il y a {} agents qui ont leur c_cir renseigné en 2012, versus 2 058 445 agents en 2012 au total".format(len(data_careers_2012.ident.unique()))

# On regarde pourquoi les corps sont parfois en NaN
data_careers_corps_NAN = data_careers[data_careers['corps'].isnull()]
data_careers_corps_NAN.c_cir.unique()
data_careers_corps_NAN_2012 = data_careers_corps_NAN[data_careers_corps_NAN['annee'] == 2012]
print "Il y a {} agents auxquels on ne parvient pas à attribuer un corps en 2012, parce qu'ils sont dans les {} grades suivants qu'on n'a pas dans la table des correspondances {}".format(len(data_careers_corps_NAN_2012.ident.unique()), len(data_careers_corps_NAN.c_cir.unique()), data_careers_corps_NAN.c_cir.unique())
# Ces NaN sont dus aux grades S09886', 'N00466', 'S08733', 'S05490', 'S10067', 'S04395'

###### Attention,  aucun identifiants n'a plusieurs codes grades pour l'année 2012
data_careers_2012_count_obs_per_ident = data_careers_2012.ident.value_counts().reset_index()
data_careers_2012_count_obs_per_ident_appearing_more_than_once = data_careers_2012_count_obs_per_ident[data_careers_2012_count_obs_per_ident['ident'] != 1]
# On trouve 0 identifiants apparaissant plusieurs fois en 2012, ie ayant plusieurs code grade neg en 2012

# On crée une colonne corps 2013 pour chaque obs en 2012
data_careers_2012 = data_careers[data_careers['annee'] == 2012]
data_careers_2012 = data_careers_2012.rename(columns = {'corps':'corps_2012', 'c_cir':'c_cir_2012'})

data_careers_2013 = data_careers[data_careers['annee'] == 2013]
data_careers_2013 = data_careers_2013.rename(columns = {'corps':'corps_2013', 'c_cir':'c_cir_2013'})

data_careers = data_careers_2012.merge(data_careers_2013, on = 'ident')
data_careers.to_csv(os.path.join(save_path, "2012_2013_c_cir.csv"))

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


# Add column transition intra corps to count_corps
dict_count_retention = data_transitions_intra_corps.set_index('corps_2012').to_dict()['share_of_transition_to_this_corps_2013_fr_corps_2012']
count_per_corps['taux de retention'] = count_per_corps['Label corps en 2012'].map(dict_count_retention)


plt.hist(pd.to_numeric(
        data_transitions_intra_corps['share_of_transition_to_this_corps_2013_fr_corps_2012']), histtype='bar', rwidth=0.3)
plt.savefig(os.path.join(fig_save_path, 'transitions_intra_corps_2012_2013_c_cir.png'), bbox_inches='tight')

data_transitions_intra_corps = data_transitions_intra_corps.sort('share_of_transition_to_this_corps_2013_fr_corps_2012')
print data_transitions_intra_corps[['corps_2012', 'count_of_idents', 'total_number_of_transitions_from_corps_2012', 'share_of_transition_to_this_corps_2013_fr_corps_2012']].head(10).to_latex()
print data_transitions_intra_corps[['corps_2012', 'count_of_idents', 'total_number_of_transitions_from_corps_2012', 'share_of_transition_to_this_corps_2013_fr_corps_2012']].head(10)['count_of_idents'].sum()
print data_transitions_intra_corps[['corps_2012', 'count_of_idents', 'total_number_of_transitions_from_corps_2012', 'share_of_transition_to_this_corps_2013_fr_corps_2012']].head(10)['total_number_of_transitions_from_corps_2012'].sum()


print data_transitions_intra_corps[['corps_2012', 'count_of_idents', 'total_number_of_transitions_from_corps_2012', 'share_of_transition_to_this_corps_2013_fr_corps_2012']].tail(10).to_latex()
print data_transitions_intra_corps[['corps_2012', 'count_of_idents', 'total_number_of_transitions_from_corps_2012', 'share_of_transition_to_this_corps_2013_fr_corps_2012']].tail(10)['count_of_idents'].sum()
print data_transitions_intra_corps[['corps_2012', 'count_of_idents', 'total_number_of_transitions_from_corps_2012', 'share_of_transition_to_this_corps_2013_fr_corps_2012']].tail(10)['total_number_of_transitions_from_corps_2012'].sum()


# Nombre d'ident représentés
data_transitions_intra_corps['count_of_idents'].sum()
# Part des idens représentés
data_transitions_intra_corps['count_of_idents'].sum() / data_corps['count_of_idents'].sum()

# GRAPHIQUE 2: part des transitions intra corps entre 2012 et 2013, pour les agents qui changent de grade enntre 2012 et 2013
data_careers_only_w_c_cir_change = data_careers[data_careers['c_cir_2012'] != data_careers['c_cir_2013']]
print "il y a {} agents qui changent de grade entre 2012 et 2013".format(len(data_careers_only_w_c_cir_change)) # 200 350

data_corps_only_w_c_cir_change = data_careers_only_w_c_cir_change[['corps_2012', 'corps_2013', 'ident']]
data_corps_only_w_c_cir_change = data_corps_only_w_c_cir_change.groupby(['corps_2012', 'corps_2013']).count().reset_index()
data_corps_only_w_c_cir_change = data_corps_only_w_c_cir_change.rename(columns = {'ident':'count_of_idents'})

# On crée une variable qui donne la part des transitions intra corps pour chaque corps
data_corps_only_w_c_cir_change['total_number_of_transitions_from_corps_2012'] = data_corps_only_w_c_cir_change['count_of_idents'].groupby(data_corps_only_w_c_cir_change['corps_2012']).transform('sum')
data_corps_only_w_c_cir_change['share_of_transition_to_this_corps_2013_fr_corps_2012'] = data_corps_only_w_c_cir_change['count_of_idents'] / data_corps_only_w_c_cir_change['total_number_of_transitions_from_corps_2012']

# On graph maintenant les probabilités de transitions au même corps entre 2012 et 2013 pour chaque corps
data_transitions_intra_corps_only_w_c_cir_change = data_corps_only_w_c_cir_change[data_corps_only_w_c_cir_change['corps_2012'] == data_corps_only_w_c_cir_change['corps_2013']]

# On ajoute une colonne taux de rétention conditionnellement à changement de grade entre 2012 et 2013
dict_count_retention_condit_cht_grade = data_transitions_intra_corps_only_w_c_cir_change.set_index('corps_2012').to_dict()['share_of_transition_to_this_corps_2013_fr_corps_2012']
count_per_corps['taux de retention si chgmt grade'] = count_per_corps['Label corps en 2012'].map(dict_count_retention_condit_cht_grade)

plt.hist(pd.to_numeric(
        data_transitions_intra_corps_only_w_c_cir_change['share_of_transition_to_this_corps_2013_fr_corps_2012']), histtype='bar', rwidth=0.3)
plt.savefig(os.path.join(fig_save_path, 'transitions_intra_corps_only_w_c_cir_change_2012_2013.png'), bbox_inches='tight')

print "{} corps sont représentés (les autres n'ont pas d'agents changeant de grade entre 2012 et 2013)".format(len(data_transitions_intra_corps_only_w_c_cir_change.corps_2012.unique()))
print "{} agents changeant de grades restent dans le corps de provenance entre 2012 et 2013".format(data_transitions_intra_corps_only_w_c_cir_change['count_of_idents'].sum())

data_transitions_intra_corps_only_w_c_cir_change = data_transitions_intra_corps_only_w_c_cir_change.sort('share_of_transition_to_this_corps_2013_fr_corps_2012')
print data_transitions_intra_corps_only_w_c_cir_change[['corps_2012', 'count_of_idents', 'total_number_of_transitions_from_corps_2012', 'share_of_transition_to_this_corps_2013_fr_corps_2012']].head(10).to_latex()
print data_transitions_intra_corps_only_w_c_cir_change[['corps_2012', 'count_of_idents', 'total_number_of_transitions_from_corps_2012', 'share_of_transition_to_this_corps_2013_fr_corps_2012']].head(10)['count_of_idents'].sum()
print data_transitions_intra_corps_only_w_c_cir_change[['corps_2012', 'count_of_idents', 'total_number_of_transitions_from_corps_2012', 'share_of_transition_to_this_corps_2013_fr_corps_2012']].head(10)['total_number_of_transitions_from_corps_2012'].sum()


print data_transitions_intra_corps_only_w_c_cir_change[['corps_2012', 'count_of_idents', 'total_number_of_transitions_from_corps_2012', 'share_of_transition_to_this_corps_2013_fr_corps_2012']].tail(10).to_latex()
print data_transitions_intra_corps_only_w_c_cir_change[['corps_2012', 'count_of_idents', 'total_number_of_transitions_from_corps_2012', 'share_of_transition_to_this_corps_2013_fr_corps_2012']].tail(10)['count_of_idents'].sum()
print data_transitions_intra_corps_only_w_c_cir_change[['corps_2012', 'count_of_idents', 'total_number_of_transitions_from_corps_2012', 'share_of_transition_to_this_corps_2013_fr_corps_2012']].tail(10)['total_number_of_transitions_from_corps_2012'].sum()

# Nombre d'ident représentés
data_transitions_intra_corps['count_of_idents'].sum()
# Part des idens représentés
data_transitions_intra_corps['count_of_idents'].sum() / data_corps['count_of_idents'].sum()

## GRAPHIQUE 3: taille des corps en 2012
data_corps_2012 = pd.DataFrame(data_careers['corps_2012'].value_counts().reset_index())
data_corps_2012 = data_corps_2012.rename(columns = {'index':'Label corps en 2012', 'corps_2012':'Nombre agents'})
print data_corps_2012.to_latex()

## GRAPHIQUE 4 : on veut maintenant savoir si les plus gros corps (ceux qui ont le plus d'agents) en retiennent le plus
pd.options.display.float_format = '{:.1}'.format
data_transitions_intra_corps_only_w_c_cir_change['share_weighted'] = data_transitions_intra_corps_only_w_c_cir_change['total_number_of_transitions_from_corps_2012'] * data_transitions_intra_corps_only_w_c_cir_change['share_of_transition_to_this_corps_2013_fr_corps_2012']
data_transitions_intra_corps_only_w_c_cir_change = data_transitions_intra_corps_only_w_c_cir_change.sort('share_of_transition_to_this_corps_2013_fr_corps_2012')

labels = data_transitions_intra_corps_only_w_c_cir_change['corps_2012']


plt.scatter(data_transitions_intra_corps_only_w_c_cir_change['total_number_of_transitions_from_corps_2012'], data_transitions_intra_corps_only_w_c_cir_change['share_of_transition_to_this_corps_2013_fr_corps_2012'])
for label, x, y in zip(labels, data_transitions_intra_corps_only_w_c_cir_change['total_number_of_transitions_from_corps_2012'], data_transitions_intra_corps_only_w_c_cir_change['share_of_transition_to_this_corps_2013_fr_corps_2012']):
    plt.annotate(
        label,
        xy=(x, y), xytext=(-20, 20),
        textcoords='offset points', ha='left', va='bottom',
        bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
        arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))

plt.savefig(os.path.join(fig_save_path, 'test.png'), bbox_inches='tight')

data_corps2 = data_corps.groupby('corps_2012')['count_of_idents'].max()
data_corps_change_corps = data_corps[data_corps['corps_2012'] != data_corps['corps_2013']]
data_corps_change_corps_max = data_corps_change_corps.groupby('corps_2012')['count_of_idents'].max().reset_index()

# merge les dataframe pour obtenir une colonne du premier corps autre que le corps de 2012 qui attire les agents
data_corps_transit_max = data_corps_change_corps_max.merge(
        data_corps_change_corps, on= ['corps_2012', 'count_of_idents'], how = 'left')
data_corps_transit_max = data_corps_transit_max.drop_duplicates('corps_2012') # garde uniquement un des grades qui maximimse nombre de transitions

dict_count_transition_other_most_attr_corps = data_corps_transit_max.set_index('corps_2012').to_dict()['share_of_transition_to_this_corps_2013_fr_corps_2012']
count_per_corps['max taux de transition vers autre corps'] = count_per_corps['Label corps en 2012'].map(dict_count_transition_other_most_attr_corps)

dict_other_most_attr_corps = data_corps_transit_max.set_index('corps_2012').to_dict()['corps_2013']
count_per_corps['autre corps ac. max taux de transition'] = count_per_corps['Label corps en 2012'].map(dict_other_most_attr_corps)


pd.options.display.float_format = '{:.1%}'.format
print count_per_corps.to_latex()
count_per_corps.to_csv(os.path.join(working_dir_path, "table_infos_corps.csv"))

labels = range(0,116)

plt.figure(num=None, figsize=(15, 15), dpi=100, facecolor='w', edgecolor='k')

plt.scatter(count_per_corps['Nombre agents'], count_per_corps['taux de retention si chgmt grade'])
for label, x, y in zip(labels, count_per_corps['Nombre agents'], count_per_corps['taux de retention si chgmt grade']):
    plt.annotate(
        label,
        xy=(x, y), xytext=(-20, 20),
        textcoords='offset points', ha='left', va='bottom',
        bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
        arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))
plt.xlabel('Effectifs', fontsize = 20)
plt.ylabel('Taux de retention conditionnellement a un changement de grade', fontsize = 20)
plt.savefig(os.path.join(fig_save_path, 'effectifs_tx_retentions_cdt_chgmt_grade.png'), bbox_inches='tight')
