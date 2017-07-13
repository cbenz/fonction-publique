# -*- coding: utf-8 -*-
from __future__ import division
import pandas as pd
import os
from fonction_publique.base import output_directory_path
import matplotlib.pyplot as plt

results = pd.read_csv(
    os.path.join(
        output_directory_path,
        'simulation_counterfactual_echelon',
        'results_annuels.csv'
        )
    )[['ident', 'annee', 'c_cir', 'echelon']].rename(columns = {'echelon':'echelon_predit'})

observed = pd.read_csv(
    os.path.join(
        output_directory_path,
        'clean_data_finalisation',
        'data_ATT_2002_2015_with_filter_on_etat_at_exit_and_change_to_filter_on_etat_grade_corrected.csv',
        )
    ).query('(annee > 2011) & (c_cir == c_cir_2011)').copy()[[
        'ident', 'annee', 'c_cir', 'echelon']].rename(columns = {'echelon':'echelon_observe'})

data = observed.merge(results, on = ['ident', 'annee', 'c_cir'], how = 'left')
data = data.query('(echelon_observe != 55555) & (echelon_predit != 55555)').copy()
data['difference'] = abs(data.echelon_observe - data.echelon_predit)

##########
share_of_good_prediction = len(data.query('echelon_predit == echelon_observe')) / len(data)
share_of_good_prediction_with_1_y_change = len(data.query('difference < 2')) / len(data)

share_of_good_prediction_by_year = []
for annee in range(2012,2016):
    data_annee = data.query('annee == @annee')
    share_of_good_prediction_by_year.append(
        len(data_annee.query('(echelon_predit == echelon_observe)')) / len(data_annee)
        )
    distribution_erreurs = (
        data_annee['echelon_observe'] - data_annee['echelon_predit']
        ).value_counts().reset_index().rename(
            columns = {'index':'difference', 0:'count'}
            )
    plt.bar(distribution_erreurs['difference'].tolist(), distribution_erreurs['count'].tolist())
    plt.show()

distribution_erreurs = (data['echelon_observe'] - data['echelon_predit']).value_counts().reset_index().rename(
    columns = {'index':'difference', 0:'count'}
    )

plt.bar(distribution_erreurs['difference'].tolist(), distribution_erreurs['count'].tolist())

###########
data['is_obs_equal_to_predit'] = (data['echelon_predit'] == data['echelon_observe']).astype(int)
data['count_n_error_by_ident'] = data.groupby('ident')['is_obs_equal_to_predit'].transform(sum)

plt.bar(data.query('annee == 2012').count_n_error_by_ident.value_counts().reset_index()['index'],
        data.query('annee == 2012').count_n_error_by_ident.value_counts().reset_index()['count_n_error_by_ident']
        )

data_ident_with_error = data.query('is_obs_equal_to_predit == 0').ident.unique().tolist()
data_ident_with_big_error = data.query(
    '(is_obs_equal_to_predit == 0) & (difference > 1) & (count_n_error_by_ident > 1)').ident.unique().tolist()

share_of_perfect_echelon_trajectory_prediction = (
    len(data.ident.unique().tolist()) - len(data_ident_with_error)
    ) / len(data.ident.unique())

share_of_good_echelon_trajectory_prediction = (
    len(data.ident.unique().tolist()) - len(data_ident_with_big_error)
    ) / len(data.ident.unique())