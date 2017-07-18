# -*- coding: utf-8 -*-
"""

Goals:
    - imputer un échelon IPP de 2011 à 2015 avec un pas trimestriel
    - créer une variable d'entrée dans le grade trimestrielle
    - créer une variable de sortie de grade trimestrielle
    - imputer un échelon contrefactuel aux agents qui quittent leur grade de 2011 entre 2011 et 2015
"""


from __future__ import division

import os
import pandas as pd
from fonction_publique.base import output_directory_path, grilles, table_corresp_grade_corps
from fonction_publique.imputation_duree_grade.clean_data_initialisation import clean_grille
from fonction_publique.base import asset_path
from fonction_publique.career_simulation_vectorized import AgentFpt, compute_changing_echelons_by_grade


def get_possible_grilles(grade, period, grilles):
    grilles = clean_grille(grilles, False, table_corresp_grade_corps)
    grille_in_effect = grilles[
        (grilles['code_grade_NETNEH'] == grade) &
        (grilles['date_effet_grille'] <= period)
        ]
    if grille_in_effect.empty:
        return None
    else:
        return grille_in_effect.date_effet_grille.max()


def reshape_wide_to_long(data):
    data = data[[
       'ident', 'annee', 'echelon',
       u'c_cir_2011', u'right_censored', u'left_censored',
       u'last_y_in_grade_bef', u'grade_bef', u'exit_status', u'next_grade', 'next_grade_corrected',
       u'last_y_observed_in_grade', u'first_y_in_next_grade',
       u'annee_min_entree_dans_grade', u'annee_max_entree_dans_grade',
       u'duree_min', u'duree_max'
       ]]
    data_carrieres = pd.read_csv(os.path.join(
        output_directory_path,
        "select_data",
        "corpsAT_1995.csv"
        )).query('annee > 2000').copy()
    data_quarterly = data.merge(data_carrieres, on = ['ident', 'annee'], how = 'inner')
    data_quarterly_long = pd.wide_to_long(
        data_quarterly, ['etat', 'ib'], i=['ident', 'annee'], j=''
        ).reset_index().rename(columns = {'':'quarter'})
    data_quarterly_long['quarter'] = data_quarterly_long['quarter'].astype(int)
    assert len(data.ident.unique()) == len(data_quarterly_long.ident.unique())
    return data_quarterly_long


def get_data_with_quarter_of_entry_in_2011_echelon(data_long, grilles):
    dict_periods = {1:'03-31', 2:'06-30', 3:'09-30', 4:'12-31'}
    data_long['period'] = pd.to_datetime(
        data_long['annee'].map(str) + '-' + data_long['quarter'].map(dict_periods).map(str)
        ).dt.strftime('%Y-%m-%d')
    data_long_echelon_2011 = data_long.query('(annee == 2011) & (quarter == 4)').copy()[[
        'ident', 'ib', 'echelon'
        ]].drop_duplicates().rename(columns = {"ib":"ib_2011", "echelon":"echelon_2011"})
    data_annee_to_look_into = data_long.query('(annee <= 2011) & (annee > last_y_in_grade_bef)').copy()
    data_annee_to_look_into_with_ib_2011 = data_long_echelon_2011.merge(
        data_annee_to_look_into,
        on = ['ident'],
        how = 'right',
        )
    data_annee_to_look_into_only_ib_2011 = data_annee_to_look_into_with_ib_2011.query(
        'ib == ib_2011'
        )
    data_annee_to_look_into_only_ib_2011['period_entry_echelon_2011'] = data_annee_to_look_into_only_ib_2011.groupby(
        'ident'
        )['period'].transform(min)
    data_input = data_annee_to_look_into_only_ib_2011.query('period == period_entry_echelon_2011').drop_duplicates()
    data_input['c_cir_2011'] = data_input['c_cir_2011'].astype(str)
    return data_input


#def impute_quarterly_echelon(data_long, grilles):
#    dict_periods = {1:'03-31', 2:'06-30', 3:'09-30', 4:'12-31'}
#    data_long['period'] = pd.to_datetime(
#        data_long['annee'].map(str) + '-' + data_long['quarter'].map(dict_periods).map(str)
#        ).dt.strftime('%Y-%m-%d')
#    cas_uniques = data_long[['c_cir', 'period']].drop_duplicates().set_index(['c_cir', 'period'])
#    liste_cas_uniques = []
#    for (c_cir, period), row in cas_uniques.iterrows():
#        date_effet = get_possible_grilles(c_cir, period, grilles)
#        liste_cas_uniques.append([c_cir, period, date_effet])
#    cas_uniques_w_date_effet = pd.DataFrame(liste_cas_uniques, columns = ['c_cir', 'period', 'date_effet_grille'])
#    data_merged = data_long.merge(cas_uniques_w_date_effet, on = ['c_cir', 'period'])
#    assert len(data_merged) == len(data_long)
#    data_merged_w_grille = data_merged.merge(grilles, on = ['c_cir', 'ib', 'date_effet_grille'], how = 'left')
#    assert len(data_merged_w_grille) == len(data_long)
#    data_merged_w_grille = data_merged_w_grille.rename(columns = {
#        'echelon_x':'echelon_CNRACL', 'echelon_y':'echelon_IPP'
#        })
#    data_merged_w_grille['echelon_IPP'] = data_merged_w_grille['echelon_IPP'].replace(
#        ['ES'], 55555
#        ).fillna(-1).astype(int)
#    return data_merged_w_grille


#def correct_quarterly_echelon_for_last_quarters_in_grade(data_long_w_echelon_IPP, grilles):
#    data_year_exit = data_long_w_echelon_IPP.query('(annee == last_y_observed_in_grade + 1)').copy()[[
#       u'ident',
#       u'annee', u'quarter', u'first_y_in_next_grade',
#       u'exit_status', u'generation', u'last_y_observed_in_grade',
#       u'libemploi', u'left_censored', 'next_grade_corrected', u'last_y_in_grade_bef',
#       u'next_grade', u'duree_min', u'grade_bef', u'right_censored',
#       u'c_cir_2011', u'duree_max', u'sexe', u'statut', u'an_aff',
#       u'annee_min_entree_dans_grade', u'annee_max_entree_dans_grade',
#       u'etat', u'ib', u'period', u'echelon_CNRACL', 'echelon_IPP',
#       ]].rename(columns = {"echelon_CNRACL":"echelon", "echelon_IPP":"echelon_IPP1"})
#    data_year_exit['c_cir'] = data_year_exit['c_cir_2011']
#    data_year_exit_with_c_cir_2011_with_echelon = impute_quarterly_echelon(data_year_exit, grilles).rename(
#        columns = {'echelon_IPP':'echelon_IPP_from_grade_2011'}
#        )
#    data_year_exit_with_c_cir_2011_with_echelon[
#        'echelon_IPP_from_grade_2011'
#        ] = data_year_exit_with_c_cir_2011_with_echelon[
#            'echelon_IPP_from_grade_2011'
#            ].fillna(-1).astype(int)
#    data_year_exit_with_c_cir_2011_with_echelon = data_year_exit_with_c_cir_2011_with_echelon[[
#        'ident', 'annee', 'quarter', 'echelon_IPP_from_grade_2011',
#        ]]
#    data_long = data_long_w_echelon_IPP.merge(
#        data_year_exit_with_c_cir_2011_with_echelon, on = ['ident', 'annee', 'quarter'], how = 'left'
#        ).rename(columns = {"echelon_IPP1":"echelon_IPP"})
#    data_long['echelon_IPP_modif_y_after_exit'] = data_long['echelon_IPP']
#    data_long.loc[data_long['echelon_IPP'] == -1, "echelon_IPP_modif_y_after_exit"] = data_long[
#        'echelon_IPP_from_grade_2011'
#        ].fillna(-1)
#    return data_long
#
#
#def get_quarter_of_grade_exit(data_long_w_echelon_IPP_corrected, grilles):
#    data_last_echelon_observed_in_grade = data_long_w_echelon_IPP_corrected.query(
#        '(annee == last_y_observed_in_grade) & (quarter == 4)'
#        )[['ident', 'echelon_IPP']].rename(
#            columns = {'echelon_IPP':'last_echelon_observed_in_grade_2011'}
#            )
#    data_last_echelon_observed_in_grade[
#        'last_echelon_observed_in_grade_2011_plus_one'
#        ] = data_last_echelon_observed_in_grade[
#            'last_echelon_observed_in_grade_2011'
#            ] + 1
#    data_merged = data_long_w_echelon_IPP_corrected.merge(
#        data_last_echelon_observed_in_grade, on = 'ident', how = 'outer'
#        )
#    data_last_y_with_info_chgmt = data_merged.query(
#        '(echelon_IPP_from_grade_2011 != -1) & (echelon_IPP == -1)'
#        ).copy() # agents sur leurs grilles de 2011 alors qu'il st en exit et introuvables sur la grille de leur nouveau grade
#    data_last_y_with_info_chgmt = data_last_y_with_info_chgmt.query(
#        '(echelon_IPP_from_grade_2011 == last_echelon_observed_in_grade_2011) | (echelon_IPP_from_grade_2011 == last_echelon_observed_in_grade_2011_plus_one)'
#        ).copy() #  agents placés au même échelon (ou cet échelon plus 1) que leur der échelon obs dans leur grade
#    data_last_y_with_info_chgmt['first_quarter_exited'] = data_last_y_with_info_chgmt.groupby(
#        'ident'
#        )['quarter'].transform(max) + 1
#    data_last_y_with_info_chgmt['first_quarter_exited'] = data_last_y_with_info_chgmt['first_quarter_exited'].replace(
#        5, 1
#        ) # set the change to be at 1st quarter for ppl with pbmatic case (
#        # i.e qu'on ne place pas dans leur grade de 2011 et pas dans leur grade de sortie le dernier trimestre de l'année suivant leur sortie
#    data_last_y_with_info_chgmt = data_last_y_with_info_chgmt[[
#        'ident',
#        'first_quarter_exited'
#        ]].drop_duplicates()
#    data_with_quarter_of_exit = data_long_w_echelon_IPP_corrected.merge(
#        data_last_y_with_info_chgmt, on = ['ident'], how = 'left'
#        )
#    data_with_quarter_of_exit['first_quarter_exited'] = data_with_quarter_of_exit[
#        'first_quarter_exited'
#        ].fillna(-1)
#    data_with_quarter_of_exit.loc[
#        (data_with_quarter_of_exit[
#            'right_censored'
#            ] == False) & (data_with_quarter_of_exit['first_quarter_exited'] == -1),
#        'first_quarter_exited'
#        ] = 1
#    data_with_quarter_of_exit['quarterly_exit_status'] = (data_with_quarter_of_exit['exit_status'] == True) & (
#        data_with_quarter_of_exit['quarter'] >= data_with_quarter_of_exit['first_quarter_exited'])
#    assert len(data_with_quarter_of_exit) == len(data_long_w_echelon_IPP_corrected)
#    return data_with_quarter_of_exit
