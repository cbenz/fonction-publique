# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 09:48:59 2017

@author: l.degalle
"""
# Filters: individuals at least one time in the corps
from __future__ import division

import os
import pandas as pd
import matplotlib.pyplot as plt

asset_path_careers = 'M:/CNRACL/clean/'
save_path = 'M:/CNRACL/output'
asset_path_corres_grades_corps = "C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/assets/corresp_neg_netneh.csv"
fig_save_path = "C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/ecrits/note_corps_Lisa/Figures/"
working_dir_path = 'C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/stat_desc/corps'

datasets = [
            'pamplemousse.h5',
           '1976_1979_carrieres.h5',
           '1970_1975_carrieres.h5',
           '1960_1965_carrieres.h5',
           '1966_1969_carrieres.h5'
           ]

# On sélectionne les obs pour l'IB du dernier trimestre,
# pour les années 2012 et 2013

where = "(annee >= 2012) & (annee <= 2013) & (trimestre = 4)"
list_data = []
for dataset in datasets:
    path = os.path.join(asset_path_careers, dataset)
    data = pd.read_hdf(path, "ib", where= where)
    data['ib'] = data['ib'].astype(int)
    list_data.append(data)
    
data_ib_careers = pd.concat(list_data)
data_ib_careers = data_ib_careers[['ident', 'ib', 'annee']]
print "{} idents au depart".format(
                                  len(data_ib_careers['ident'].unique())
                                  )

# On supprime les observations qui ont un IB non renseigné ou nul pour l'une
# des deux années. On supprime les duplicates
data_ib_careers = data_ib_careers.drop_duplicates()
data_ib_careers = data_ib_careers[~data_ib_careers['ib'].isin(['', 0, -1])]

count_data_ib_careers = data_ib_careers.groupby('ident').count()
print "{} idents n'ont pas d'ib rens. sur les 2 années".format(
        len(count_data_ib_careers.query(
                'annee != 2'
                ).reset_index()['ident'].unique())
        )
count_data_ib_careers_full = count_data_ib_careers.query('annee == 2')
list_idents_keep = count_data_ib_careers_full.reset_index()['ident'].tolist()

data_ib_careers = data_ib_careers[
        data_ib_careers['ident'].isin(list_idents_keep)
        ]
print "{} idents leur ib rens. sur les 2 années".format(
        len(data_ib_careers['ident'].unique())
        )



# On crée les variables ib_2012 et ib_2013
data_ib_careers_2012 = data_ib_careers.query('annee == 2012').rename(
        columns = {'ib':'ib_2012'})
data_ib_careers_2013 = data_ib_careers.query('annee == 2013').rename(
        columns = {'ib':'ib_2013'})

data_ib_careers = data_ib_careers_2012.merge(
        data_ib_careers_2013, on = 'ident'
        )
data_ib_careers = data_ib_careers[['ident', 'ib_2012', 'ib_2013']]

# On fusionne ces données sur les IB avec les données c_cir qu'on a nettoyées
# dans le fichier select_data_corps_w_c_cir.py pour pouvoir
# imputer un corps.
data_c_cir_careers = pd.read_csv(
        os.path.join(save_path, "2012_2013_c_cir.csv")
        )

data_c_cir_careers = data_c_cir_careers.drop(
        ['Unnamed: 0', 'annee_x', 'annee_y'], 1
        )

data_careers = data_ib_careers.merge(
        data_c_cir_careers, on = "ident", how = "inner"
        )

"{} identifiants après fusion entre données ib et c_cir".format(
        len(data_careers['ident'].unique())
        )

# On veut obtenir la part de la somme des ib de chaque corps dans la somme
# des ib pour chaque corps.
data_careers['sum_ib_2012'] = [data_careers['ib_2012'].sum()] * len(
        data_careers
        )

data_sum_ib_corps = data_careers.groupby(
        'corps_2012'
        )['ib_2012'].sum().reset_index()
data_sum_ib_corps = data_sum_ib_corps.rename(
        columns = {"ib_2012": "sum_ib_per_corps_2012"}
        )

data_careers = data_careers.merge(
        data_sum_ib_corps, how = 'left', on = "corps_2012"
        )




plt.figure(figsize=(7, 7))



hist = True
if hist:
    # On fusionne le tableau d'informations sur les corps issues des c_cir 
    # avec les informations sur les ib
    data_c_cir_corps = pd.read_csv(
        os.path.join(working_dir_path, "table_infos_corps.csv")
        )
    
    dict_corps_tx = data_c_cir_corps.set_index("Label corps en 2012").to_dict()[
            "taux de retention si chgmt grade"
            ]
    data_careers['taux_ret_condit_corps'] = data_careers['corps_2012'].map(
            dict_corps_tx
            )
    
    data_c_cir_corps = data_c_cir_corps.reset_index()
    dict_eff = data_c_cir_corps.set_index("Label corps en 2012").to_dict()[
            "Nombre agents"
            ]
    
    data_careers['effectifs'] = data_careers['corps_2012'].map(dict_eff)
    
    fig = plt.figure(figsize=(7, 7), dpi=100, facecolor='w', edgecolor='k')
    plt.subplot(232)
    data_careers.taux_ret_condit_corps.plot(kind='hist', histtype='bar',
                                            bins = 20)
    plt.ylabel('')
    plt.title("1 obs = 1 agent",  y=1.08, fontsize = 14)



hist_weighted_IB = True
if hist_weighted_IB:
    data_careers_cc_tx_ret = data_careers[
            ~data_careers['taux_ret_condit_corps'].isnull()
            ]
    plt.subplot(233)
#    fig = plt.figure(figsize=(7, 7), dpi=100, facecolor='w', edgecolor='k')
    data_careers_cc_tx_ret.taux_ret_condit_corps.plot(
            kind= 'hist',
            weights = data_careers_cc_tx_ret['ib_2012'],
            histtype = 'bar',
            bins = 20)
    plt.ylabel('')
    plt.title("1 obs = 1 IB",  y=1.08, fontsize = 14)
    

hist_corps = True
if hist_corps:
    data_corps = data_careers[['corps_2012', 'taux_ret_condit_corps']].drop_duplicates()
    plt.subplot(231)
    data_corps.taux_ret_condit_corps.plot(
            kind= 'hist',
            histtype = 'bar',
            bins = 20,  y=1.08)
    plt.title("1 obs = 1 corps", y=1.08, fontsize = 14)
    plt.ylabel("Compte", fontsize = 14)
    fig.subplots_adjust(hspace=0.2, wspace=0.8)

plt.savefig(
    os.path.join(fig_save_path, 'hist_tx_retention_conditionnels.pdf'),
    format='pdf',
    bbox_inches='tight'
    )

data_careers['share_ib_corps_2012'] = data_careers[
        'sum_ib_per_corps_2012'
        ] / data_careers['sum_ib_2012']

data_careers = data_careers.sort('share_ib_corps_2012', ascending = False)

data_ib_corps = data_careers[[
        'corps_2012', 'share_ib_corps_2012'
        ]].drop_duplicates()

data_ib_corps['cum_share_ib_corps_2012'] = data_ib_corps[
        'share_ib_corps_2012'
        ].cumsum()

data_ib_corps = data_ib_corps.reset_index()
data_ib_corps = data_ib_corps.drop('index', 1)
data_ib_corps = data_ib_corps.rename(
        columns = {"corps_2012": "Label corps en 2012"}
        )

# On fusionne le tableau d'informations sur les corps issues des c_cir 
# avec les informations sur les ib
data_c_cir_corps = pd.read_csv(
        os.path.join(working_dir_path, "table_infos_corps.csv")
        )

data = data_c_cir_corps.merge(data_ib_corps, on = "Label corps en 2012")
data = data.drop('Unnamed: 0', 1)
data = data[[u'Label corps en 2012', u'Nombre agents', u'Part du total',
       u'Part cumulee du total', u'share_ib_corps_2012',
       u'cum_share_ib_corps_2012', u'taux de retention',
       u'taux de retention si chgmt grade',
       u'max taux de transition vers autre corps',
       u'autre corps ac. max taux de transition']]

print data.to_latex()
