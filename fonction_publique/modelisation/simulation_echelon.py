# -*- coding: utf-8 -*-
from __future__ import division

import os
import pandas as pd
from fonction_publique.base import output_directory_path, grilles, table_corresp_grade_corps
from fonction_publique.imputation_duree_grade.clean_data_initialisation import clean_grille
from fonction_publique.base import asset_path, project_path, output_directory_path, grilles
from fonction_publique.career_simulation_vectorized import AgentFpt, compute_changing_echelons_by_grade
from fonction_publique.imputation_duree_grade.to_quarterly import (
    get_data_with_quarter_of_entry_in_2011_echelon,
    reshape_wide_to_long,
    )

#def format_data_as_input_for_career_simulation_vectorized(data_long_w_echelon_IPP_corrected_and_quarter_of_exit):
#    data_last_echelon_observed = data_long_w_echelon_IPP_corrected_and_quarter_of_exit.query(
#        '(quarterly_exit_status == False) & (right_censored == False)'
#        ).copy()
#    data_last_echelon_observed[
#        'last_y_observed_in_grade_corrected'
#        ] = data_last_echelon_observed.groupby('ident')['annee'].transform(max)
#    data_input = data_last_echelon_observed.query('(annee == last_y_observed_in_grade_corrected)')
#    data_last_echelon_observed[
#        'last_quarter_observed_in_grade'
#        ] = data_input.groupby('ident')['quarter'].transform(max)
#    data_input = data_last_echelon_observed.query(
#        '(annee == last_y_observed_in_grade_corrected) & (quarter == last_quarter_observed_in_grade)'
#        )
#    data_input = data_input[['ident', 'echelon_IPP_modif_y_after_exit']]
#    data_input2 = data_long_w_echelon_IPP_corrected_and_quarter_of_exit.merge(
#        data_input, on = ['ident', 'echelon_IPP_modif_y_after_exit'], how = 'inner'
#        ).query('quarterly_exit_status == False').copy()
#    data_input2['first_y_in_last_echelon'] = data_input2.groupby('ident')['annee'].transform(min)
#    data_input2 = data_input2.query('annee == first_y_in_last_echelon').copy()
#    data_input2['first_quarter_in_last_echelon'] = data_input2.groupby('ident')['quarter'].transform(min)
#    data_input2 = data_input2.query('quarter == first_quarter_in_last_echelon').copy()
#    print data_input2.head()
#    dict_codes_grades = {'TTH1':793, 'TTH2':794, 'TTH3':795, 'TTH4':796}
#    data_input2 = data_input2[['ident', 'period', 'c_cir_2011', 'echelon_IPP_modif_y_after_exit']].rename(
#        columns = {'echelon_IPP_modif_y_after_exit':'echelon'})
#    data_input2['grade'] = data_input2['c_cir_2011'].map(dict_codes_grades)
#    data_input2.grade = data_input2.grade.astype(int)
#    data_input2.echelon = data_input2.echelon.astype(int)
#    return data_input2


def get_data(rebuild = True):
    if rebuild or not(os.path.exists('data_input3.csv')):
        data = pd.read_csv(os.path.join(
            output_directory_path,
            "clean_data_finalisation",
            "data_ATT_2002_2015_with_filter_on_etat_at_exit_and_change_to_filter_on_etat_grade_corrected.csv")
            )
        del data['Unnamed: 0']
        data_long = reshape_wide_to_long(data)
        data_long_with_quarter_of_entry_in_2011_echelon = get_data_with_quarter_of_entry_in_2011_echelon(
            data_long,
            grilles
            )
        del data_long_with_quarter_of_entry_in_2011_echelon['echelon']
        data_long_with_quarter_of_entry_in_2011_echelon['echelon'] = data_long_with_quarter_of_entry_in_2011_echelon[
            'echelon_2011'
            ]
        data_long_with_quarter_of_entry_in_2011_echelon['grade'] = data_long_with_quarter_of_entry_in_2011_echelon[
            'c_cir_2011'
            ].map(
                {'TTH1':793 ,'TTH2':794, 'TTH3':795, 'TTH4': 796}
                )
        del data_long_with_quarter_of_entry_in_2011_echelon['c_cir']
#        data_long = reshape_wide_to_long(data)
#        data_long_w_echelon_IPP = impute_quarterly_echelon(data_long, grilles)
#        data_long_w_echelon_IPP_corrected = correct_quarterly_echelon_for_last_quarters_in_grade(
#            data_long_w_echelon_IPP, grilles
#            )
#        data_long_w_echelon_IPP_corrected_and_quarter_of_exit = get_quarter_of_grade_exit(
#            data_long_w_echelon_IPP_corrected,
#            grilles
#            )
#        data_input2 = format_data_as_input_for_career_simulation_vectorized(
#            data_long_w_echelon_IPP_corrected_and_quarter_of_exit
#            ).query('(echelon != -1) & (echelon != 55555)').copy().head(50)
        print('saving')
        data_long_with_quarter_of_entry_in_2011_echelon.dtypes
        print data_long_with_quarter_of_entry_in_2011_echelon.echelon.dtype
        data_long_with_quarter_of_entry_in_2011_echelon.to_csv('data_input3.csv')
    else:
        print('reading')
        data_long_with_quarter_of_entry_in_2011_echelon = pd.read_csv('data_input3.csv')
        print data_long_with_quarter_of_entry_in_2011_echelon.dtypes
    return data_long_with_quarter_of_entry_in_2011_echelon[[
        'ident', 'period', 'grade', 'echelon'
        ]].copy().drop_duplicates()


#if __name__ == '__main__':
#    import logging
#    import sys
#    logging.basicConfig(level = logging.DEBUG, stream = sys.stdout)
#    data_input = get_data(rebuild = False)[[
#        'ident', 'period', 'grade', 'echelon'
#        ]]
#    data_input['period'] = pd.to_datetime(data_input['period'])
#    data_input = data_input.query('echelon != 55555').copy()
#    grilles['code_grade'] = grilles['code_grade'].astype(int)
#    grilles = grilles[grilles['code_grade'].isin([793, 794, 795, 796])].copy()
#    grilles['echelon'] = grilles['echelon'].replace(['ES'], -2).astype(int)
#    agents = AgentFpt(data_input, end_date = pd.Timestamp(2017, 01, 01))
#    agents.set_grille(grilles)
#    agents.compute_result()
#
#    resultats = agents.result
#    resultats_annuel = resultats[resultats['quarter'].astype(str).str.contains("-12-31")].copy()
##    assert resultats_annuel.groupby('ident')['quarter'].count().unique() == 5
#    resultats_annuel['annee'] = pd.to_datetime(resultats_annuel['quarter']).dt.year
#    resultats_annuel['c_cir'] = resultats_annuel['grade'].map({793:'TTH1' ,794:'TTH2', 795:'TTH3', 796:'TTH4'})
#    del resultats_annuel['period']
#    del resultats_annuel['quarter']
#
#    resultats_annuel.to_csv(os.path.join(
#        output_directory_path,
#        'simulation_counterfactual_echelon',
#        'results_annuels_apres_modification_etat_initial.csv'
#        )
#    )

