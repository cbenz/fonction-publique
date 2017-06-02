# -*- coding: utf-8 -*-
"""
Created on Wed May 31 10:20:44 2017

@author: l.degalle
"""

import os
import pandas as pd
import numpy as np
from fonction_publique.base import project_path, output_directory_path, grilles
from clean_data_initialisation import clean_careers


def merge_data_bef_aft_2011(data_bef_2011_path):
    """ Merge data before 2011 and after 2011, clean data types and add generation group var """
    data_carrieres = pd.read_csv(os.path.join(
        output_directory_path,
        "select_data",
        "corpsAT_1995.csv",
        )).query('annee > 2001')
    data_carrieres_clean = clean_careers(data_carrieres, 'ATT', True, 1960, grilles)
    data_aft_2011 = data_carrieres_clean.query('annee > 2010')
    data_bef_2011 = pd.read_csv(data_bef_2011_path)
    del data_bef_2011['corps_NETNEH']
    time_invarying_var = data_aft_2011[['ident', 'an_aff', 'sexe', 'generation']].drop_duplicates()
    data_bef_2011 = data_bef_2011.merge(time_invarying_var, on = ['ident'])
    data = data_aft_2011.append(data_bef_2011)
    data['echelon'] = data['echelon'].fillna(-1).replace(
        to_replace='ES', value=55555, inplace=False
        ).astype(float).astype(int)
    del data['etat']
    data_etat = data_carrieres_clean.query('annee > 2001')[['ident', 'annee', 'etat']]
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


def get_exit_status_and_next_grade(data):
    """ Create var indicating exit status and next grade, if known """
    data['exit_status'] = (data['c_cir'] != data['c_cir_2011']) & (data['annee'] > 2010).astype(bool)
    data = data.sort_values(['ident', 'annee'])
    data['next_grade'] = data.groupby(['ident'])['c_cir'].transform('last')
    data.loc[data.next_grade == data.c_cir_2011, ['next_grade']] = None
    data = data[(data['c_cir'] == data['c_cir_2011']) | (data['indicat_ch_grade'])]
    return data


def get_var_duree_min_duree_max(data):
    """ Create var indicating duration min and max (if known) in grade """
    data_max_entree_dans_grade = data.query(
        'indicat_ch_grade == True'
        ).groupby('ident')['annee'].max().reset_index().rename(columns={'annee':'annee_max_bef_entree_dans_grade'})
    data = data.merge(data_max_entree_dans_grade, on = ['ident'], how = 'outer')
    data['annee_max_entree_dans_grade'] = (data['annee_max_bef_entree_dans_grade'] + 1).fillna(-1).astype(int)
    del data['annee_max_bef_entree_dans_grade']
    data_min_entree_dans_grade = data.query(
        'indicat_ch_grade == True'
        ).groupby('ident')['annee'].min().reset_index().rename(columns={'annee':'annee_min_bef_entree_dans_grade'})
    data = data.merge(data_min_entree_dans_grade, on = ['ident'], how = 'outer')
    data['annee_min_entree_dans_grade'] = (data['annee_min_bef_entree_dans_grade'] + 1).fillna(-1).astype(int)
    del data['annee_min_bef_entree_dans_grade']
    data = data.set_index(['ident', 'annee']).sort_index()
    data = data.reset_index()
    data['last_year_in_c_cir_or_observed'] = data.groupby(['ident'])['annee'].transform('last').astype(int)
    data['duree_min'] = data['last_year_in_c_cir_or_observed'] - data['annee_max_entree_dans_grade'] + 1
    data.loc[
        data['annee_max_entree_dans_grade'] == -1, ['duree_min']
        ] = data['last_year_in_c_cir_or_observed'] - 2002
    data['duree_max'] = data['last_year_in_c_cir_or_observed'] - data['annee_min_entree_dans_grade'] + 1
    data.loc[data['left_censored'] == True, ['duree_max']] = -1
    data.loc[data['right_censored'] == True, ['duree_max']] = -1
    data['is_in_duree_min'] = (
        (data['annee'] >= (data['annee_max_entree_dans_grade'])) & (data['c_cir'] == data['c_cir_2011'])
        )
    data = data.set_index(['ident', 'annee']).sort_index()
    return data


def main(data_bef_2011_path, output_filename):
    data_merged = merge_data_bef_aft_2011(data_bef_2011_path)
    data_merged_w_censoring = get_censoring(data_merged)
    data_merged_w_censoring_and_exit = get_exit_status_and_next_grade(data_merged_w_censoring)
    data_merged_w_censoring_and_exit_and_durations = get_var_duree_min_duree_max(data_merged_w_censoring_and_exit)
    data_merged_w_censoring_and_exit_and_durations.to_csv(
        os.path.join(output_directory_path, "clean_data_finalisation", output_filename))

if __name__ == '__main__':
    data_bef_2011_path = os.path.join(
        output_directory_path,
        "imputation",
        "data_2003_2011_new_method_4.csv"
        )
    main(data_bef_2011_path, "data_ATT_2002_2015.csv")


data = pd.read_csv(os.path.join(
        output_directory_path,
        "imputation",
        "data_2003_2011.csv"
        ))