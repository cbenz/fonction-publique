# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
from fonction_publique.base import grilles, output_directory_path

grilles = grilles[grilles['code_grade_NETNEH'].isin(['TTM1', 'TTH1', 'TTH2', 'TTH3', 'TTH4'])]
data_counterfactual_echelon_trajectory = pd.read_csv(
    os.path.join(
        output_directory_path,
        'simulation_counterfactual_echelon',
        'results_annuels.csv'
        )
    )
del data_counterfactual_echelon_trajectory['Unnamed: 0']


def predict_next_period_grade_when_exit_to_other_corps(data):
    data.loc[
        (data['next_situation'] == 'exit_oth') |
        (
            (data['grade'] == 'TTH4') &
            (data['next_situation'] == 'exit_next')
            ),
        'next_grade'
        ] = "TTM1"
    data['next_annee'] = data['annee'] + 1
    return data


def predict_echelon_next_period_when_no_exit(data):
    data_no_exit = data.query("next_situation == 'no_exit'").copy()
    data_no_exit['next_grade'] = data_no_exit['grade']
    data_no_exit['next_annee'] = data_no_exit['annee'] + 1
    data_no_exit = data_no_exit.merge(
        data_counterfactual_echelon_trajectory[['ident', 'annee', 'echelon']].rename(
            columns = {'annee': 'next_annee', 'echelon': 'next_echelon'}
            ),
        on = ['ident', 'next_annee'],
        how = 'left',
        )
    return data_no_exit


def predict_echelon_next_period_when_exit(data, grilles):
    data_exit = data.query("next_situation != 'no_exit'").copy()
    data_exit.loc[(data_exit['next_situation'] == 'exit_next'), 'next_grade'] = [
        'TTH' + str(int(s[-1:]) + 1) for s in data_exit.query("next_situation == 'exit_next'")['grade']
        ]
    data_exit['next_grade'] = data_exit['next_grade'].replace(['TTH5'], 'TTM1')
    grilles_in_effect = (grilles
        .query("date_effet_grille <= 2012")
        .groupby(['code_grade_NETNEH'])
        .agg({'date_effet_grille': np.max})
        .reset_index()
        )
    grilles = grilles.merge(
        grilles_in_effect,
        on = ['code_grade_NETNEH', 'date_effet_grille'],
        how = 'inner'
        )
    # TODO: these echelon_x and echelon_y are ugly
    data_exit_merged = data_exit.merge(grilles, left_on = 'next_grade', right_on = 'code_grade_NETNEH', how = 'inner')
    data_exit_merged['next_echelon'] = data_exit_merged['echelon_y'].replace(['ES'], 55555).astype(int)
    data_exit_merged['echelon'] = data_exit_merged['echelon_x'].astype(int)
    del data_exit_merged['echelon_x']
    del data_exit_merged['echelon_y']

    data_exit_echelon_pour_echelon = data_exit_merged.query("(next_grade != 'TTH4') & (echelon == next_echelon)")
    data_exit_ib_pour_ib = data_exit_merged.query("next_grade == 'TTH4'") # To generalize

    data_exit_ib_pour_ib = (data_exit_ib_pour_ib
        .query('ib_y >= ib_x')
        .groupby(['ident']).agg({'ib_y': np.min})
        .reset_index()
        )
    data_exit_with_ib_pour_ib = data_exit.merge(data_exit_ib_pour_ib, on = ['ident'], how= 'inner')
    data_exit_with_ib_pour_ib = data_exit_with_ib_pour_ib.merge(
        grilles[['code_grade_NETNEH', 'ib', 'echelon']].rename(columns = {'ib': 'next_ib', 'echelon': 'next_echelon'}),
        left_on = ['ib_y', 'next_grade'],
        right_on = ['next_ib', 'code_grade_NETNEH'],
        how = 'left')
    del data_exit_with_ib_pour_ib['code_grade_NETNEH']
    del data_exit_with_ib_pour_ib['ib_y']

    data_exit_with_echelon_pour_echelon = data_exit_echelon_pour_echelon.query('echelon == next_echelon').copy().rename(
        columns = {"ib_x": "ib", "ib_y": "next_ib"})
    print len(data_exit_with_echelon_pour_echelon)
    print len(data_exit_with_echelon_pour_echelon.ident.unique())
    data_exit_with_echelon_pour_echelon_right_col = data_exit_with_echelon_pour_echelon[data_exit_with_ib_pour_ib.columns]

    data_exit = data_exit_with_echelon_pour_echelon_right_col.append(data_exit_with_ib_pour_ib)

    data_exit['next_echelon'] = data_exit['next_echelon'].astype(int)
#    data_missing_echelon_next = data.query("next_situation != 'no_exit'")[~
#        data.query("next_situation != 'no_exit'")['ident'].isin(
#            data_exit.ident.unique().tolist()
#            )
#        ]
#    print data_missing_echelon_next.grade.unique()
#    data_missing_echelon_next['next_ib'] = 446
#    data_missing_echelon_next['next_echelon'] = 11 #tofix
#    assert (data_missing_echelon_next.grade.unique().tolist() == ['TTH4']) & (
#            data_missing_echelon_next.next_grade.unique().tolist() == ['TTM1']
#            )
#    data_exit = data_exit.append(data_missing_echelon_next)
    # assert len(data_exit.ident.unique()) == len(data.query("next_situation != 'no_exit'"))
    print data_exit[~data_exit['ident'].isin(data.query("next_situation != 'no_exit'").ident.unique().tolist())]
    return data_exit


def get_ib(data, grilles):
    grilles['echelon'] = grilles['echelon'].replace(['ES'], 55555).astype(int)
    grilles_grouped = (grilles
        .query('date_effet_grille <= 2012')
        .groupby(['code_grade_NETNEH', 'echelon'])
        .agg({'date_effet_grille': np.max})
        .reset_index()
        )
    grilles_to_use = grilles_grouped.merge(
        grilles,
        on = ['code_grade_NETNEH', 'echelon', 'date_effet_grille'],
        how = 'inner'
        )
    grilles_to_use['code_grade_NETNEH'] = grilles_to_use['code_grade_NETNEH'].astype(str)
    data['grade'] = data['grade'].astype(str)
    data_merged = data.merge(
        grilles_to_use[['code_grade_NETNEH', 'echelon', 'ib']],
        left_on = ['grade', 'echelon'],
        right_on = ['code_grade_NETNEH', 'echelon'],
        how = 'left',
        )[
            ['ident', 'annee', 'grade', 'echelon', 'ib', 'situation']
            ]
    return data_merged


def main(data, results_filename, grilles):
    del data['Unnamed: 0']
    data = data.query('echelon != 55555').copy()
    data_with_next_grade_when_exit_to_other = predict_next_period_grade_when_exit_to_other_corps(data)
    data_with_next_echelon_when_no_exit = predict_echelon_next_period_when_no_exit(
        data
        )
    data_with_next_echelon_when_exit = predict_echelon_next_period_when_exit(
        data_with_next_grade_when_exit_to_other, grilles
        )
    results = data_with_next_echelon_when_no_exit.append(data_with_next_echelon_when_exit)
    assert len(results.query("(next_situation != 'no_exit') & (next_grade != 'TTH4') & (echelon != next_echelon)")) == 0
    results = results[['ident', 'next_annee', 'next_grade', 'next_echelon', 'next_situation']]
    results['next_annee'] = results['next_annee'].astype(int)
    results['ident'] = results['ident'].astype(int)
    results['next_grade'] = results['next_grade'].astype(str)
    results = results.rename(columns={col: col.replace('next_', '') for col in results.columns})
    assert len(list(set(results.ident.unique()) - set(data.ident.unique()))) == 0
    results = get_ib(results, grilles)
    results['grade'] = results['grade'].astype(str)
    results.to_csv(os.path.join('M:/CNRACL/simulation/results_modif_regles_replacement', results_filename))


if __name__ == '__main__':
    for model in ['_m0', '_m1', '_m2']:
        main(data = pd.read_csv('M:/CNRACL/simulation/data_simul_2011{}.csv'.format(model)),
             results_filename = 'results_2011{}.csv'.format(model),
             grilles = grilles
             )
