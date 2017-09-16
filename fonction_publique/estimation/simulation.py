# -*- coding: utf-8 -*-


import argparse
import logging
import os
import sys

import numpy as np
import pandas as pd

from fonction_publique.base import (grilles, output_directory_path, simulation_directory_path)
from fonction_publique.career_simulation_vectorized import AgentFpt

log = logging.getLogger(__name__)


def get_data_counterfactual_echelon_trajectory(data = None):
    if data is None:
        data_counterfactual_echelon_trajectory = pd.read_csv(
            os.path.join(
                output_directory_path,
                'simulation_counterfactual_echelon',
                'results_annuels.csv'
                )
            )
        del data_counterfactual_echelon_trajectory['Unnamed: 0']
    return data_counterfactual_echelon_trajectory


def predict_next_period_grade_when_exit_to_other_corps(data):
    log.info('Predict next period grade when exit to other corps')
    data.loc[
        (data['next_situation'] == 'exit_oth') |
        (
            (data['grade'] == 'TTH4') &
            (data['next_situation'] == 'exit_next')
            ),
        'next_grade'
        ] = "TTM1"
    data['next_annee'] = data['annee'] + 1
    data['next_anciennete_dans_echelon'] = 5
    return data

def predict_echelon_next_period_when_no_exit(data):
    log.debug('Predict echelon next period when no exit')
    log.debug("1. Number of idents = {} and number of lines is {}".format(
        len(data.ident.unique()), len(data.ident)))
    data_no_exit = data.query("next_situation == 'no_exit'").copy()
    log.debug("2. Number of idents = {} and number of lines is {}".format(
        len(data_no_exit.ident.unique()), len(data_no_exit.ident)))
    data_no_exit['next_grade'] = data_no_exit['grade']
    data_no_exit['period'] = pd.to_datetime(data_no_exit['annee'].astype(str) + "-12-31")
    predicted_year = data_no_exit['annee'].max() + 1
    log.info('Echelon prediction when no exit for year {}'.format(predicted_year))
    data_no_exit['anciennete_dans_echelon'] = 5
    # FIXME the latter should be more provided by the model
    # Replace by the following
    data_no_exit['code_grade_NETNEH'] = data_no_exit['grade']
    data_no_exit.drop(['grade', 'next_annee', 'next_grade', 'next_anciennete_dans_echelon'], axis = 1, inplace = True)
    #    data_input = get_data(rebuild = False)[[
    #        'ident', 'period', 'grade', 'echelon'
    #        ]]
    #    data_input['period'] = pd.to_datetime(data_input['period'])
    #    data_input = data_input.query('echelon != 55555').copy()
    assert len(data_no_exit['annee'].unique()) == 1
    annee = data_no_exit['annee'].unique()[0]
    agents_grilles = (grilles
        .loc[grilles['code_grade_NETNEH'].isin(['TTM1', 'TTH1', 'TTH2', 'TTH3', 'TTH4'])]
        .copy()
        )
    agents_grilles['code_grade_NEG'] = agents_grilles['code_grade_NEG'].astype(int)
    # FIXME very ugly way of dealing with echelon spéciaux of TTH4
    agents_grilles['echelon'] = agents_grilles['echelon'].replace([-5], 8).astype(int)
    log.debug("3. Number of idents = {} and number of lines is {}".format(
        len(data_no_exit.ident.unique()), len(data_no_exit.ident)))
    filtered_grilles = (agents_grilles
        .query('annee_effet_grille > @annee')[['code_grade_NETNEH', 'code_grade_NEG']]
        .drop_duplicates()
        )
    assert (filtered_grilles.code_grade_NETNEH.value_counts() == 1).all()
    data_no_exit = data_no_exit.merge(
        filtered_grilles,
        on = 'code_grade_NETNEH',
        how = 'left',
        )
    log.debug("4. Number of idents = {} and number of lines is {}".format(
        len(data_no_exit.ident.unique()), len(data_no_exit.ident)))
    data_no_exit['grade'] = data_no_exit['code_grade_NEG']
    del data_no_exit['code_grade_NEG']
    # agents_grilles = agents_grilles.loc[agents_grilles['code_grade_NEG'].isin([793, 794, 795, 796])].copy()
    # grilles['echelon'] = grilles['echelon'].replace(['ES'], -2).astype(int)
    log.debug("5. Number of idents = {} and number of lines is {}".format(
        len(data_no_exit.ident.unique()), len(data_no_exit.ident)))
    agents = AgentFpt(data_no_exit, end_date = pd.Timestamp(predicted_year + 1, 1, 1))  # < end_date
    agents.set_grille(agents_grilles)
    agents.compute_result()
    resultats = agents.result
    resultats_annuel = resultats[resultats.quarter.astype(str).str.contains("-12-31")].copy()
    assert resultats_annuel.groupby('ident')['quarter'].count().unique() == 1, resultats_annuel.groupby('ident')['quarter'].count().unique()
    resultats_annuel['next_annee'] = pd.to_datetime(resultats_annuel['quarter']).dt.year  # Au 31 décembre de l'année précédente
    resultats_annuel.rename(columns = {
        'echelon': 'next_echelon',
        'anciennete_dans_echelon_bis': 'next_anciennete_dans_echelon',
        },
        inplace = True,
        )
    # next_grade should be a string
    resultats_annuel['next_grade'] = resultats_annuel['grade'].map({793: 'TTH1', 794: 'TTH2', 795: 'TTH3', 796: 'TTH4'})
    del resultats_annuel['period']
    del resultats_annuel['quarter']

    # print len(data_no_exit)
    data_no_exit = data_no_exit.merge(
        resultats_annuel[['ident', 'next_annee', 'next_grade', 'next_echelon', 'next_anciennete_dans_echelon']],
        on = ['ident'],
        how = 'left',
        )
    return data_no_exit


def predict_echelon_next_period_when_exit_next_grade(data, grilles):
    log.debug('Predict echelon next period when exit')
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
    data_exit_ib_pour_ib = data_exit_merged.query("next_grade == 'TTH4'")  # To generalize

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

    data_exit_with_echelon_pour_echelon_right_col = data_exit_with_echelon_pour_echelon[
        data_exit_with_ib_pour_ib.columns]

    data_exit = data_exit_with_echelon_pour_echelon_right_col.append(data_exit_with_ib_pour_ib)

    data_exit['next_echelon'] = data_exit['next_echelon'].astype(int)
    # FIXME Some anciennete_dans_echelon are NA: we set them to 9 the median value
    data_exit['anciennete_dans_echelon'].fillna(9, inplace = True)
    # FIXME hypothèse de conseravtion de la durée dans l'échelon à la promotion
    data_exit['next_anciennete_dans_echelon'] = data_exit['anciennete_dans_echelon'].astype(int) + 12

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
    # print data_exit[~data_exit['ident'].isin(data.query("next_situation != 'no_exit'").ident.unique().tolist())]
    return data_exit


def get_ib(data, grilles):
    annees = data.annee.unique()
    assert len(annees) == 1
    annee = annees[0]
    grilles = grilles.copy()
    # grilles['echelon'] = grilles['echelon'].replace(['ES'], 55555).astype(int)  # FIXME or drop me
    grilles_grouped = (grilles
        .query('annee_effet_grille <= @annee')
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
            ['ident', 'annee', 'grade', 'echelon', 'anciennete_dans_echelon', 'ib', 'situation']
            ]
    return data_merged


def predict_next_period(data = None, grilles = None):
    """
    data is the resut of the first simulation du grade for the nex year
    Take data and compute the echelon and IB for next year
    """
    assert data is not None
    assert grilles is not None
    del data['Unnamed: 0']
    data = data.query('echelon != 55555').copy()
    data_with_next_grade_when_exit_to_other = predict_next_period_grade_when_exit_to_other_corps(data)
    data_with_next_echelon_when_no_exit = predict_echelon_next_period_when_no_exit(
        data
        )
    data_with_next_echelon_when_exit = predict_echelon_next_period_when_exit_next_grade(
        data_with_next_grade_when_exit_to_other, grilles
        )
    results = data_with_next_echelon_when_no_exit.append(data_with_next_echelon_when_exit)
    assert len(results.query("(next_situation != 'no_exit') & (next_grade != 'TTH4') & (echelon != next_echelon)")) == 0
    results = results[['ident', 'next_annee', 'next_grade', 'next_echelon', 'next_situation', 'next_anciennete_dans_echelon']].copy()
    results['next_annee'] = results['next_annee'].astype(int)
    results['ident'] = results['ident'].astype(int)
    results['next_grade'] = results['next_grade'].astype(str)
    results = results.rename(columns = {col: col.replace('next_', '') for col in results.columns})
    assert len(list(set(results.ident.unique()) - set(data.ident.unique()))) == 0
    results = get_ib(results, grilles)
    results['grade'] = results['grade'].astype(str)
    print results.head(50)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-file', default = '2011_data_simul_withR_MNL_1.csv', help = 'input file (csv)')
    parser.add_argument('-o', '--output-file', default = 'results_2011_m1.csv', help = 'output file (csv)')
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    parser.add_argument('-d', '--debug', action = 'store_true', default = False, help = "increase output verbosity (debug mode)")

    args = parser.parse_args()
    if args.verbose:
        level = logging.INFO
    elif args.debug:
        level = logging.DEBUG
    else:
        level = logging.WARNING
    logging.basicConfig(level = level, stream = sys.stdout)
    input_file_path = os.path.join(simulation_directory_path, 'results',
        args.input_file
        )
    log.info('Using unput data from {}'.format(input_file_path))
    data = pd.read_csv(input_file_path)
    results = predict_next_period(data = data, grilles = grilles)
    directory_path = os.path.join(simulation_directory_path, 'results')
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    output_file_path = os.path.join(directory_path, args.output_file)
    log.info("Saving results to {}".format(output_file_path))
    results.to_csv(output_file_path)


if __name__ == '__main__':
    sys.exit(main())
    # logging.basicConfig(level = logging.DEBUG, stream = sys.stdout)
    # for model in ['_m1']:  #, '_m2', '_m3']:
    #     data = pd.read_csv(os.path.join(
    #         output_directory_path,
    #         '..',
    #         'simulation',
    #         'data_simul_2011{}.csv'.format(model)
    #         ))
    #     predict_next_period(
    #         data = data,
    #         results_filename = 'results_2011{}.csv'.format(model),
    #         grilles = grilles,
    #         )
