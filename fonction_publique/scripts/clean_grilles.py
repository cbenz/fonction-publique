# -*- coding:utf-8 -*-


from __future__ import division

import logging
import pandas as pd
import numpy as np
import os
import sys

from fonction_publique.base import (
    focus_grille_xlsx_path, grilles_path, grilles_txt_path, grilles_hdf_path, table_correspondance_corps_path
    )

app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)

dtype_by_variable = {
    "categh": str,
    "code_grade_NEG": str,
    "code_grade_NETNEH": str,
    "date_effet_grille": str,
    "echelle": str,
    "echelon": str,
    "ib": float,
    "libelle_grade_NEG": str,
    "max_mois": float,
    "min_mois": float,
    "moy_mois": float,
    }


def check_grilles():
    """
    Check the coherence betwenn the following grilles:
        grilles_txt_path (neg_pour_ipp.txt): almost exhaustive grilles
        focus_grille_xlsx_path (corresp_neg_netneh_2018.xlsx): focus sample with additonal date_fin,  columns
    """
    exhaustive = pd.read_table(
        grilles_txt_path,
        dtype = dtype_by_variable,
        usecols = [
            'categh',
            'code_grade_NEG',
            'code_grade_NETNEH',
            'date_effet_grille',
            'echelle',
            'echelon',
            'ib',
            'libelle_grade_NEG',
            'max_mois',
            'min_mois',
            'moy_mois',
            ],
        )
    exhaustive['date_effet_grille'] = pd.to_datetime(
        exhaustive['date_effet_grille'],
        dayfirst = True,
        infer_datetime_format = True
        )

    focus = pd.read_excel(
        focus_grille_xlsx_path,
        dtype = dtype_by_variable,
        )
    focus['date_effet_grille'] = pd.to_datetime(
        focus['date_effet_grille'],
        dayfirst = True,
        infer_datetime_format = True
        )

    commn_variables = set(focus.columns).intersection(set(exhaustive.columns))

    # Strip zeros from some variable in focus
    focus['echelle'] = focus['echelle'].str.lstrip('0')
    focus['echelle'].replace({'nan': np.nan}, inplace = True)
    focus['code_grade_NEG'] = focus['code_grade_NEG'].str.lstrip('0')

    # Strip ending spaces in libelle_grade_NEG
    focus['libelle_grade_NEG'] = focus['libelle_grade_NEG'].str.rstrip(' ')
    exhaustive['libelle_grade_NEG'] = exhaustive['libelle_grade_NEG'].str.rstrip(' ')

    problematic_variables = list()
    for variable in commn_variables:
        differences = set(focus[variable].unique()).difference(set(exhaustive[variable].unique()))
        if differences:
            problematic_variables.append(variable)
            print variable
            print differences
            print '\n'

    for variable in problematic_variables:
        print variable
        print focus[variable].unique()
        print exhaustive[variable].unique()
        print '\n'


def clean_grille(force_rebuild = False, hdf_path = grilles_hdf_path):
    """ Extract relevant data from neg_pour_ipp.txt and change to convenient dtype then save to HDFStore."""
    if force_rebuild is True:
        grille = pd.read_table(
            grilles_txt_path,
            dtype = {
                "categh": str,
                "code_grade_NEG": str,
                "code_grade_NETNEH": str,
                "date_effet_grille": str,
                "echelle": str,
                "echelon": str,
                "ib": float,
                "libelle_grade_NEG": str,
                "max_mois": float,
                "min_mois": float,
                "moy_mois": float,
                },
            usecols = [
                'categh',
                'code_grade_NEG',
                'code_grade_NETNEH',
                'date_effet_grille',
                'echelle',
                'echelon',
                'ib',
                'libelle_grade_NEG',
                'max_mois',
                'min_mois',
                'moy_mois',
                ]
            )

        # Filter some invalid IB's
        grille = grille[~grille['ib'].isin([-1, 0])].copy()

        # Set special echelons to -5
        special_echelons = list(
            set(grille.echelon.unique()) - set([str(n).zfill(2) for n in range(1, 25)] + [str(n) for n in range(1, 25)])
            )
        grille.loc[grille['echelon'].isin(special_echelons), 'echelon'] = '-5'

        # Creating anne_grille as int. Missing integers are coded as -1
        grille['date_effet_grille'] = (
            pd.to_datetime(
                grille['date_effet_grille'],
                dayfirst = True,
                infer_datetime_format = True
                )
            .dt.year
            .fillna(-1)
            .astype('int32')
            )
        # Missing integers are coded as -1
        for col in [
                'echelon',
                'ib',
                'max_mois',
                'min_mois',
                'moy_mois'
                ]:
            grille[col] = grille[col].fillna(-1).astype('int32')

        for col in [
                'categh',
                'code_grade_NEG',
                'code_grade_NETNEH',
                'echelle',
                'libelle_grade_NEG',
                ]:
            grille[col] = grille[col].fillna(-1).astype(str)

        corresp_grade_corps = pd.read_csv(
            table_correspondance_corps_path,
            usecols = [
                'CadredemploiNEG',
                'cadredemploiNETNEH',
                'CodeEmploiGrade_neg',
                ],
            dtype = {
                'CadredemploiNEG': str,
                'cadredemploiNETNEH': str,
                'CodeEmploiGrade_neg': str,
                },
            sep = ';',
            ).rename(columns = {
                'CadredemploiNEG': 'corps_NEG',
                'cadredemploiNETNEH': 'corps_NETNEH',
                'CodeEmploiGrade_neg': 'code_grade_NEG',
                })
        corresp_grade_corps['code_grade_NEG'] = [s.lstrip("0") for s in corresp_grade_corps['code_grade_NEG']]
        grille = grille.merge(corresp_grade_corps, on = 'code_grade_NEG', how = 'left')
        grille.to_hdf(hdf_path, 'grilles', format = 'table', data_columns = True, mode = 'w')
        return True
    else:
        if os.path.exists(hdf_path):
            log.info('Using existing {}'.format(hdf_path))
            return True
        else:
            clean_grille(force_rebuild = True, hdf_path = hdf_path)


def main():
    # clean_grille(force_rebuild = True, hdf_path = os.path.join(grilles_path, 'grilles.h5'))
    check_grilles()

if __name__ == "__main__":
    sys.exit(main())
