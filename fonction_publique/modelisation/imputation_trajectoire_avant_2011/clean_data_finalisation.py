# -*- coding: utf-8 -*-
"""
Created on Thu May 04 16:02:50 2017

@author: l.degalle
"""

from __future__ import division
import os
import pandas as pd
import numpy as np
from clean_data_initialisation import clean_grille, clean_data_carriere_initial, merge_careers_w_grille

# Paths
fonction_publique_path = r"C:\Users\l.degalle\CNRACL\fonction-publique\fonction_publique\\"
careers_asset_path = r"M:\CNRACL\output\bases_AT_imputations_trajectoires_avant_2011"
results_asset_path = os.path.join(fonction_publique_path, "modelisation\imputation_trajectoire_avant_2011")

# Data carrières de 2007 à 2015
data_carrieres = pd.read_csv(
    os.path.join(careers_asset_path, "corpsAT_2007.csv")
    ).query("annee >= 2007")
data_carrieres = clean_data_carriere_initial(data_carrieres, 'ATT', True, 1960)

# Data durées dans le grade
data_durees_imputees = pd.read_csv(
    os.path.join(results_asset_path, "resultats_imputation.csv")
        )

def clean_data_durees_2007_2011(data_durees_imputees):
    # On attribue une durée min et max dans le grade, avec un statut d'ambiguité pour la durée max, la durée min
    # étant par définition incertaine
    data_durees_imputees = data_durees_imputees[[
        "ident",
        "duree_initiale_dans_le_grade.1",
        "duree_initiale_dans_le_grade",
        "duree_initiale_dans_le_grade.2",
        "duree_initiale_dans_le_grade.3",
        "ambiguite_2010",
        "ambiguite_2009",
        "ambiguite_2008",
        "ambiguite_2007"
        ]].set_index("ident")

    data_durees_imputees['min_duration_in_grade'] = data_durees_imputees[[
       "duree_initiale_dans_le_grade",
       "duree_initiale_dans_le_grade.1",
       "duree_initiale_dans_le_grade.2",
       "duree_initiale_dans_le_grade.3"
       ]].min(axis=1)

    data_durees_imputees['max_duration_in_grade'] = data_durees_imputees[[
       "duree_initiale_dans_le_grade",
       "duree_initiale_dans_le_grade.1",
       "duree_initiale_dans_le_grade.2",
       "duree_initiale_dans_le_grade.3"
       ]].max(axis=1)

    data_durees_imputees = data_durees_imputees.reset_index()

    data_ambiguite = []

    data_durees_ecart = data_durees_imputees.reset_index()

    for cas in range(len(data_durees_ecart)):
        data_durees_cas = data_durees_ecart.iloc[cas]
        ident = data_durees_cas['ident']

        if data_durees_cas['min_duration_in_grade'] == 0:
            data_ambig_min = data_durees_cas['ambiguite_2010']
        elif data_durees_cas['min_duration_in_grade'] == 1:
            data_ambig_min = data_durees_cas['ambiguite_2009']

        elif data_durees_cas['min_duration_in_grade'] == 2:
            data_ambig_min = data_durees_cas['ambiguite_2008']

        else:
            data_ambig_min = data_durees_cas['ambiguite_2007']

        if data_durees_cas['max_duration_in_grade'] == 0:
            data_ambig_max = data_durees_cas['ambiguite_2010']
        elif data_durees_cas['max_duration_in_grade'] == 1:
            data_ambig_max = data_durees_cas['ambiguite_2009']
        elif data_durees_cas['max_duration_in_grade'] == 2:
            data_ambig_max = data_durees_cas['ambiguite_2008']
        else:
            data_ambig_max = data_durees_cas['ambiguite_2007']

        data_ambiguite.append([ident, data_ambig_min, data_ambig_max])

    data_ambiguite = pd.DataFrame(
        data_ambiguite,
        columns = ['ident', 'ambig_duree_min', 'ambig_duree_max']
        ).drop_duplicates()

    data_durees_imputees = data_durees_imputees.merge(data_ambiguite, on = 'ident', how = 'left')

    data_durees_imputees['ambig_duree_max'] = data_durees_imputees['ambig_duree_max'].fillna(value=False).astype('bool')
    data_durees_imputees['ambig_duree_min'] = data_durees_imputees['ambig_duree_min'].fillna(value=False).astype('bool')

    data_durees_imputees = data_durees_imputees[[
        "ident",
        "min_duration_in_grade",
        "max_duration_in_grade",
        "ambig_duree_min",
        "ambig_duree_max"
        ]]

    # Correction to fix: on sait que les agents qui sont en ambiguité max = True sont en fait des
    # agents qui ne changent pas de grade sur la période, et qui doivent être supprimés de ce dataset
    print len(data_durees_imputees.ident.unique())
    data_durees_imputees = data_durees_imputees.query('ambig_duree_max == False')
    print len(data_durees_imputees.ident.unique())
    return data_durees_imputees


def merge_data_durees_2007_2011_and_careers_2011_2015(data_durees_imputees, data_carrieres):
# On fusionne maintenant les données sur les durées initiales et les carrières
    data = data_carrieres.merge(data_durees_imputees, on = 'ident')
    return data


def tidy_data_2007_2015(data, duree_min):
    "retourne données mergées 2007 2015 avec une ligne = un individu année"
    if duree_min:
        data['duree_initiale_en_2011'] = data['min_duration_in_grade']
    else:
        data['duree_initiale_en_2011'] = data['max_duration_in_grade']
    durees = data.duree_initiale_en_2011.unique().tolist()
    data_clean = []
    for duree in durees:
        data_par_duree = data.query('duree_initiale_en_2011 == {}'.format(duree))
        data_par_duree_group = data_par_duree.groupby('ident').tail(duree + 5)
        data_clean.append(data_par_duree_group)
    data_clean = pd.concat(data_clean)
    data_clean['c_cir_impute_2007_2011'] = data_clean.groupby('ident')['c_cir'].transform('first')
    data_clean_aft_2011 = data_clean.query('annee > 2011')
    data_clean_bef_2011 = data_clean.query('annee <= 2011')
    data_clean_bef_2011.c_cir.fillna(
        data_clean_bef_2011.c_cir_impute_2007_2011, inplace = True
        )
    data_clean = data_clean_bef_2011.append(data_clean_aft_2011).sort(['ident', 'annee'])
    del data_clean['c_cir_impute_2007_2011']
    return data_clean

def impute_indicatrice_de_sortie_de_grade(data, duree_min):
    data.c_cir.fillna('out', inplace = True)

    data['first_year_in_index'] = data.groupby('ident')['annee'].transform('first')
    data = data.set_index(['ident', 'annee'])

    data = data.sort_index()
    data['past_c_cir'] = data.groupby(level=0)['c_cir'].shift(1); data
    data = data.reset_index()
#    data['c_cir_equal_next_c_cir'] = (data['c_cir'] == data['past_c_cir'])
#
#    data['exit_status'] = (data['c_cir_equal_next_c_cir'] == False) & (data['annee'] != data['first_year_in_index']) #| (data['etat'] == 0)
#    del data['c_cir_equal_next_c_cir']
    data['grade_de_2011'] = data.groupby('ident')['c_cir'].transform('first')

    data['exit_status'] = data['c_cir'] != data['grade_de_2011']
#    del data['first_year_in_index']
    data['exit_status'] = data['exit_status'].astype(int)

    data = data[(data['exit_status'] == 0) | (data['exit_status'] == 1) & (data['past_c_cir'] == data['grade_de_2011'])]

    data['next_grade'] = data.groupby(['ident'])['c_cir'].transform('last')

#    data_group = data.groupby(
#            ['ident', 'c_cir']
#            )['annee'].value_counts().rename(columns={"annee":"annee2"}).reset_index().sort(['ident', 'annee'])
#    print data_group.head(25)
#    del data_group[0]
#    data_group = data_group.groupby(
#        ['ident'])['c_cir'].value_counts(dropna = False).rename(columns={'c_cir':'c_cir_2'}).reset_index().rename(
#            columns = {0:'compte_c_cir'})
##    data_group['next_grade'] =  data_group.groupby(
##        ['ident']).c_cir.nth(2).dropna()
#
#    data_group['duree_dans_grade_de_2011'] = data_group.groupby('ident')['compte_c_cir'].transform('first')
#    data_group = data_group[['ident', 'duree_dans_grade_de_2011']]
#    data = data.merge(data_group, on = 'ident', how = 'left').drop_duplicates()
    data_ident_grade_de_2011 = data[['ident', 'grade_de_2011']].drop_duplicates().rename(columns={'grade_de_2011':'c_cir'})

    data_2011_2015 = data.query('annee > 2010')
    data_2011_2015_group = data_2011_2015.groupby('ident')['c_cir'].value_counts().rename(
        columns = {'c_cir':'c_cir2'}
        ).reset_index()
    data_2011_2015_group = data_2011_2015_group.rename(columns = {0:'duration_in_grade_from_2011'})

    data_duration_in_grade_from_2011 = data_ident_grade_de_2011.merge(
        data_2011_2015_group, on = ['ident', 'c_cir'], how = 'inner'
        )

    data = data.merge(data_duration_in_grade_from_2011, on = ['ident'], how = 'left')
    del data['c_cir_y']
    del data['past_c_cir']
    data = data.rename(columns = {"c_cir_x":"c_cir"})

    data_2015 = data.query('annee == 2015')
    idents_with_right_censoring = data_2015[data_2015['grade_de_2011'] == data_2015['c_cir']].ident.unique()

    data['right_censoring'] = data.ident.isin(idents_with_right_censoring)

    return data

#def impute_indicatrice_de_duree_legale_requise_passee_dans_grade(data, duree_min)

def main(data_durees_imputees, data_carrieres, duree_min):
    data_durees_imputees = clean_data_durees_2007_2011(data_durees_imputees)
    data = merge_data_durees_2007_2011_and_careers_2011_2015(data_durees_imputees, data_carrieres)
#    compte_nan = pd.DataFrame(data[data['c_cir'].isnull()].groupby('annee')['c_cir'].value_counts(dropna = False))
    data_tidy = tidy_data_2007_2015(data, duree_min)
    data_tidy_with_dummy_exit = impute_indicatrice_de_sortie_de_grade(data_tidy, True)
    data_tidy_with_dummy_exit.to_csv("M:/CNRACL/output/base_AT_clean_2007_2011/base_AT_clean.csv")
    return


if __name__ == '__main__':
    main(data_durees_imputees, data_carrieres, True)