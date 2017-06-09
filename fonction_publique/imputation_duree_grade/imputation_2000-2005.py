# -*- coding: utf-8 -*-
"""
Created on Wed May 24 14:58:54 2017

@author: l.degalle
"""

from __future__ import division

import numpy as np
import os
import pandas as pd
from fonction_publique.base import output_directory_path, project_path, grilles_path
from imputation_2005_2006 import (
    clean_grilles_pre_ATT,
    clean_careers_annee_annee_bef_bef_2006,
    get_cas_uniques,
    get_grilles_en_effet,
    get_indicatrice_de_changement_de_grade_2005_2006,
    merge_cas_uniques_with_grades_2005_2006,
    map_cas_uniques_2005_2006_to_data,
    )
from clean_data_initialisation import clean_careers, clean_grille, get_careers_chgmt_grade_annee_annee_bef

table_corresp_grade_corps = pd.read_csv(
    os.path.join(grilles_path, 'corresp_neg_netneh.csv'),
    delimiter = ';'
    )
corresp_grilles_ATT_et_pre_ATT = pd.read_csv(os.path.join(grilles_path, "neg_grades_supp.csv"),
                                             delimiter = ';')
grilles = pd.read_hdf(
    os.path.join(grilles_path, 'grilles_fonction_publique/grilles_old.h5')
    )
grilles = clean_grille(grilles, False, table_corresp_grade_corps)

grilles_pre_ATT = pd.read_table(
    os.path.join(grilles_path, 'grilles_fonction_publique/neg_pour_ipp.txt')
    )

data_carrieres_1995_2015 = pd.read_csv(
    "M:/CNRACL/output/bases_AT_imputations_trajectoires_1995_2011/corpsAT_1995.csv"
    )
data_carrieres_1995_2015 = clean_careers(
    data_carrieres_1995_2015,
    'ATT',
    True,
    1960,
    grilles,
    )

def main():
    annees = list(reversed(range(2001, 2006)))
    data_chgmt_2000_2005 = []
    for annee in annees:
        if annee == 2005:
            data = pd.read_csv(
                os.path.join(output_directory_path, "base_AT_clean_2006_2011/data_non_changement_grade_2005_2006.csv")
                )
        else:
            data = data_non_chgmt
        careers = clean_careers_annee_annee_bef_bef_2006(data, data_carrieres_1995_2015, annee)
        cas_uniques = get_cas_uniques(careers, annee)
        cas_uniques_w_grade = merge_cas_uniques_with_grades_2005_2006(cas_uniques, annee)
        data_w_indic_chgmt = map_cas_uniques_2005_2006_to_data(
            careers,
            cas_uniques,
            annee,
            )[[
                'ident',
                'c_cir_2006_predit',
                'indicat_ch_grade_{}'.format(annee-1),
                'ambiguite_{}'.format(annee-1),
                'etat_{}'.format(annee-1),
                'ib_{}'.format(annee-1),
                'an_aff_x',
                ]].drop_duplicates().rename(columns = {'an_aff_x':'an_aff'})
        data_chgmt = get_careers_chgmt_grade_annee_annee_bef(data_w_indic_chgmt, True, annee)
        data_chgmt_2000_2005.append(data_chgmt)
        data_non_chgmt = get_careers_chgmt_grade_annee_annee_bef(data_w_indic_chgmt, False, annee)
    data_chgmt = pd.concat(data_chgmt_2000_2005)
    data_non_chgmt.to_csv(
        os.path.join(output_directory_path, "base_AT_clean_2000_2005/data_non_changement_grade_2000_2005.csv")
        )
    data_chgmt.to_csv(
        os.path.join(output_directory_path, "base_AT_clean_2000_2005/data_changement_grade_2000_2005.csv")
        )
    return data_chgmt