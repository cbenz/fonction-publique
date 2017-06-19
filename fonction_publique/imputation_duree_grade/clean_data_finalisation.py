# -*- coding: utf-8 -*-
"""
Created on Wed May 31 10:20:44 2017

@author: l.degalle
"""

import os
import pandas as pd
from fonction_publique.base import output_directory_path, grilles
from clean_data_initialisation import clean_careers, get_echelon_after_2011_from_c_cir


def merge_data_bef_aft_2011(data_bef_2011_path, data_careers, data_aft_2011_w_echelon):
    """ Merge data before 2011 and after 2011, clean data types and add generation group var """
    data_bef_2011 = pd.read_csv(data_bef_2011_path)
    del data_bef_2011['Unnamed: 0']
    ident_keep = data_bef_2011.ident.unique().tolist()
    data_aft_2011 = data_aft_2011_w_echelon[data_aft_2011_w_echelon['ident'].isin(ident_keep)]
    del data_bef_2011['corps_NETNEH']
    time_invarying_var = data_aft_2011[['ident', 'an_aff', 'sexe', 'generation']].drop_duplicates()
    data_bef_2011 = data_bef_2011.merge(time_invarying_var, on = ['ident'])
    del data_bef_2011['index']
    del data_aft_2011['echelon_CNRACL']
    data = data_aft_2011.append(data_bef_2011)
    data['echelon'] = data['echelon'].fillna(-1).replace(
        to_replace='ES', value=55555, inplace=False
        ).astype(float).astype(int)
    del data['etat']
    data_etat = data_careers.query('annee > 2001')[['ident', 'annee', 'etat4']].rename(
        columns = {'etat4':'etat'}
        )
    data = data.merge(data_etat, on = ['ident', 'annee'], how = 'inner')
    data['generation_group'] = data['generation'].apply(str).str[2:3]
    data['generation_group'] = data['generation_group'].astype('category')
    data['generation'] = data.generation.fillna(-1)
    data['c_cir'] = data['c_cir'].fillna('out').astype(str)
    data = data[['ident',
                 'annee',
                 'sexe',
                 'generation',
                 'generation_group',
                 'an_aff',
                 'etat',
                 'c_cir',
                 'ib',
                 'echelon',
                  'date_effet_grille',
                 'min_mois',
                 'max_mois',
                 'indicat_ch_grade',
                 'ambiguite',
                 ]]
    return data


def get_censoring(data):
    """ Create var indicating left and right censoring  """
    data = data.merge(data.query('annee == 2011')[['ident', 'c_cir']], on = 'ident').rename(
        columns = {'c_cir_x':'c_cir', 'c_cir_y':'c_cir_2011'}
        )
    data_2015 = data.query('annee == 2015')
    data_2002 = data.query('annee == 2002')
    idents_with_right_censoring = data_2015[data_2015['c_cir_2011'] == data_2015['c_cir']].ident.unique()
    idents_with_left_censoring = data_2002[data_2002['c_cir_2011'] == data_2002['c_cir']].ident.unique()
    data['right_censored'] = data.ident.isin(idents_with_right_censoring)
    data['left_censored'] = data.ident.isin(idents_with_left_censoring)
    return data


def get_bef_grade(data):
    data = data.sort_values(['ident', 'annee'])
    data['last_y_in_grade_bef'] = data.groupby('ident')['annee'].transform('first')
    data_grade_bef = data.query('(annee == last_y_in_grade_bef) & (ambiguite == False) & (indicat_ch_grade == True)')[[
        'ident', 'c_cir'
        ]].rename(
            columns = {"c_cir": "grade_bef"}
            )
    data = data.merge(data_grade_bef, on = 'ident', how = 'outer')
    data['grade_bef'] = data['grade_bef'].fillna(-1)
    assert len(data.query('left_censored == True')) == len(data.query('grade_bef == -1'))
    return data


def get_exit_status_and_next_grade(data):
    """ Create var indicating exit status and next grade, if known """
    data['exit_status'] = (data['c_cir'] != data['c_cir_2011']) & (data['annee'] > 2010).astype(bool)
    data = data.sort_values(['ident', 'annee'])
    data['next_grade'] = data.groupby(['ident'])['c_cir'].transform('last')
    data.loc[data.next_grade == data.c_cir_2011, ['next_grade']] = None
    data_spell = data[(data['c_cir'] == data['c_cir_2011']) | (data['indicat_ch_grade'])]
    data_spell = data_spell.groupby('ident')['annee'].max().reset_index().rename(
        columns = {'annee':'last_y_observed_in_grade'}
        )
    data_spell['first_y_in_next_grade'] = data_spell['last_y_observed_in_grade'] + 1
    data_merged = data.merge(data_spell, on = 'ident')
    data_merged = data_merged.query('annee <= first_y_in_next_grade')
    data_merged.loc[data_merged.first_y_in_next_grade == 2016, ['first_y_in_next_grade']] = None
    return data_merged


def get_var_duree_min_duree_max(data):
    """ Create var indicating duration min and max (if known) in grade """
    data['annee_min_entree_dans_grade'] = data.groupby('ident')['annee'].transform('first').astype(int) + 1
    data.loc[data['left_censored'] == True, ['annee_min_entree_dans_grade']] = -1

    data_ambiguite = data.query('ambiguite == True')
    data_ambiguite['annee_max_entree_dans_grade'] = data_ambiguite.groupby(
        'ident'
        )['annee'].transform('last').astype(int) + 1
    data_ambiguite = data_ambiguite[['ident', 'annee_max_entree_dans_grade']].drop_duplicates()
    data = data.merge(data_ambiguite, on = 'ident', how = 'outer')
    data['annee_max_entree_dans_grade'] = data['annee_max_entree_dans_grade'].fillna(-1)
    data.loc[data['annee_max_entree_dans_grade'] == -1, ['annee_max_entree_dans_grade']] = data[
        'annee_min_entree_dans_grade'
        ]
    assert len(data.query('(left_censored == True) & (annee_min_entree_dans_grade != 1)') == 0)
    assert len(data.groupby('ident')['annee_max_entree_dans_grade'].value_counts()) == len(data.ident.unique())
    data['duree_min'] = data['last_y_observed_in_grade'] - data['annee_max_entree_dans_grade'] + 1
    data.loc[data['annee_max_entree_dans_grade'] == -1, ['duree_min']] = -1
    data['duree_max'] = data['last_y_observed_in_grade'] - data['annee_min_entree_dans_grade'] + 1
    data.loc[data['annee_min_entree_dans_grade'] == -1, ['duree_max']] = -1
    assert len(data['duree_max'] == -1) == len(data['left_censored'] == True)
    assert not data.query(
        '(ambiguite == True) & (annee_min_entree_dans_grade == -1)'
        ).duree_min.equals(data['duree_max'])
    assert len(data.query(
        '(left_censored == False) & (duree_min == -1)'
        )) == 0
    assert len(data.query(
        '(left_censored == False) & (duree_max == -1)'
        )) == 0
    return data


def filter_on_echelon(data):
    ident_to_del = data.query('(echelon == -1) & (annee > 2010) & (annee <= last_y_observed_in_grade)').ident.unique()
    data = data[~data['ident'].isin(ident_to_del)]
    return data


def filter_on_etat_when_in_grade(data):
    ident_to_del = data.query(
        '(etat != 1) & (annee >= annee_min_entree_dans_grade) & (annee <= last_y_observed_in_grade)'
        ).ident.unique()
    data = data[~data['ident'].isin(ident_to_del)]
    return data


def filter_on_etat_when_exit_status(data):
    ident_to_del = data.query('(etat != 1) & (exit_status == True)').ident.unique()
    data = data[~data['ident'].isin(ident_to_del)]
    return data


def main(data_bef_2011_path, output_filename):
    data_aft_2011_w_echelon = get_echelon_after_2011_from_c_cir(
        pd.read_csv(os.path.join(
            output_directory_path,
            "select_data",
            "corpsAT_1995.csv",
            )).query('annee > 2001'),
        grades_2011 = ['TTH1', 'TTH2', 'TTH3', 'TTH4', 'STH1', 'STH2', 'STH3', 'STH4'],
        )
    data_merged = merge_data_bef_aft_2011(
        data_bef_2011_path, pd.read_csv(os.path.join(
            output_directory_path,
            "select_data",
            "corpsAT_1995.csv",
            )).query('annee > 2001'),
        data_aft_2011_w_echelon
        )
    data_merged_w_censoring = get_censoring(data_merged)
    data_merged_w_censoring_and_grade_bef = get_bef_grade(data_merged_w_censoring)
    data_merged_w_censoring_and_exit = get_exit_status_and_next_grade(data_merged_w_censoring_and_grade_bef)
    data_merged_w_censoring_and_exit_and_durations = get_var_duree_min_duree_max(data_merged_w_censoring_and_exit)
    print len(data_merged_w_censoring_and_exit_and_durations.ident.unique())
    data_merged_w_filter_on_echelon = filter_on_echelon(data_merged_w_censoring_and_exit_and_durations)
    print len(data_merged_w_filter_on_echelon.ident.unique())
    data_merged_w_filter_on_echelon_etat_when_in_grade = filter_on_etat_when_in_grade(data_merged_w_filter_on_echelon)
    print len(data_merged_w_filter_on_echelon_etat_when_in_grade.ident.unique())
    data_merged_w_filter_on_echelon_etat_when_in_grade_when_exit_status = filter_on_etat_when_exit_status(
        data_merged_w_filter_on_echelon_etat_when_in_grade
        )
    print len(data_merged_w_filter_on_echelon_etat_when_in_grade_when_exit_status.ident.unique())
#    data_clean_bis.to_csv(
#        os.path.join(output_directory_path, "clean_data_finalisation", output_filename))


if __name__ == '__main__':
    data_bef_2011_path = os.path.join(
        output_directory_path,
        "imputation",
        "data_2003_2011_6.csv"
        )
    main(data_bef_2011_path, "data_ATT_2002_2015_with_filter_on_etat_at_exit_and_change_to_filter_on_etat.csv")


x = pd.read_csv(os.path.join(output_directory_path, "clean_data_finalisation", "data_ATT_2002_2015_solve_exit_other.csv"))