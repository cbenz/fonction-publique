# -*- coding:utf-8 -*-


from __future__ import division

import logging
import pandas as pd
import numpy as np
import os
from fonction_publique.base import grilles_txt_path, grilles_hdf_path, table_correspondance_corps_path

app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


def clean_grille(force_rebuild = False):
    """ Extract relevant data from neg_pour_ipp.txt and change to convenient dtype then save to HDFStore."""
    if force_rebuild is True:
        grille = pd.read_table(
            grilles_txt_path,
            dtype = {
                "echelon": str,
                "echelle": str,
                "categh": str,
                "code_grade_NEG": str,
                "code_grade_NETNEH": str,
                "date_effet_grille": str,
                "ib": float,
                "libelle_grade_NEG": str,
                "min_mois": float,
                "max_mois": float,
                "moy_mois": float,
                },
            usecols = [
                'echelon',
                'echelle',
                'categh',
                'code_grade_NEG',
                'code_grade_NETNEH',
                'date_effet_grille',
                'ib',
                'libelle_grade_NEG',
                'max_mois',
                'min_mois',
                'moy_mois',
                ]
            )
        grille['date_effet_grille'] = pd.to_datetime(grille['date_effet_grille'])
        grille = grille[~grille['ib'].isin([-1, 0])].copy()
        special_echelons = list(
            set(grille.echelon.unique()) - set([str(n).zfill(2) for n in range(1,25)] + [str(n) for n in range(1,25)])
            )
        grille.loc[grille['echelon'].isin(special_echelons), 'echelon'] = '-5'
        grille['annee_effet_grille'] = (pd.to_datetime(np.array(
            grille.date_effet_grille.astype(str),
            dtype = 'datetime64[Y]'
            ))).year
        for col in ['ib', 'max_mois', 'min_mois', 'moy_mois', 'echelon', 'annee_effet_grille']:
            grille[col] = grille[col].fillna(-1).astype('int32')
        for col in ['libelle_grade_NEG', 'code_grade_NEG', 'categh', 'echelle', 'code_grade_NETNEH']:
            grille[col] = grille[col].fillna(-1).astype(str)
        corresp_grade_corps =  pd.read_csv(
            table_correspondance_corps_path,
            usecols = [
                'CodeEmploiGrade_neg',
                'CadredemploiNEG',
                'cadredemploiNETNEH',
                ],
            dtype = {
                'CodeEmploiGrade_neg': str,
                'CadredemploiNEG': str,
                'cadredemploiNETNEH': str,
                },
            sep = ';',
            ).rename(columns = {
                'CodeEmploiGrade_neg':'code_grade_NEG',
                'CadredemploiNEG':'corps_NEG',
                'cadredemploiNETNEH':'corps_NETNEH'
                })
        corresp_grade_corps['code_grade_NEG'] = [s.lstrip("0") for s in corresp_grade_corps['code_grade_NEG']]
        grille = grille.merge(corresp_grade_corps, on = 'code_grade_NEG', how = 'left')
        grille.to_hdf(grilles_hdf_path, 'grilles', format = 'table', data_columns = True, mode = 'w')
        return True
    else:
        if os.path.exists(grilles_hdf_path):
            log.info('Using existing {}'.format(grilles_hdf_path))
            return True
        else:
            grilles_hdf_path(force_rebuild = True)


if __name__ == "__main__":
     clean_grille(force_rebuild = True)