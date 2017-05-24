# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 18:32:28 2017

@author: l.degalle
"""

from __future__ import division

import numpy as np
import os
import pandas as pd
from clean_data_initialisation import (
    clean_grille,
    clean_careers,
    merge_careers_with_grilles,
    clean_careers_annee_annee_bef,
    get_career_transitions_uniques_annee_annee_bef,
    get_careers_chgmt_grade_annee_annee_bef,
    )
from imputation_indicatrice_chgmt_grade_annee_annee_bef import (
    get_indicatrice_chgmt_grade_annee_annee_bef,
    map_transitions_uniques_annee_annee_bef_to_data,
    )
from fonction_publique.base import output_directory_path


def clean_grilles_pre_ATT(table_corresp_grade_corps, grilles_pre_ATT):
    """
    Nettoie les grilles des grades ayant fusionné dans le corps des ATT en 2006 (donnés par PJ),
    avec une colonne corps NETNEH (adjoint techniques territoriaux), le nom du grade d'arrivée dans le corps des ATT
    en 2006 (TTH1, TTH2 etc.) et un corps_impute_par_IPP, qui rassemble les agents venant d'un corps technique,
    de salubrité, ou de gardiens d'immeubles.
    TOFIX: à fusionner avec clean_grille

    Parameters:
    ----------
    `grilles_pre_ATT`: dataframe
    `table_corresp_grade_corps`: dataframe

    Returns:
    ----------
    dataframe
    """
    grade_NEG_bef_TTH1 = [27, 35, 391, 625, 769]
    grade_NEG_bef_TTH2 = [26, 34, 626]
    grade_NEG_bef_TTH3 = [25, 33, 627]
    grade_NEG_bef_TTH4 = [157, 156, 628]
    grades_NEG_bef_ATT = grade_NEG_bef_TTH1 + grade_NEG_bef_TTH2 + grade_NEG_bef_TTH3 + grade_NEG_bef_TTH4
    grades_NEG_bef_ATT = map(str, grades_NEG_bef_ATT)
    grilles_pre_ATT = grilles_pre_ATT[grilles_pre_ATT['code_grade_NEG'].isin(grades_NEG_bef_ATT)]
    grilles_pre_ATT['CodeEmploiGrade_neg'] = grilles_pre_ATT['code_grade_NEG'].str.zfill(4)
    grilles_pre_ATT_w_corps = grilles_pre_ATT.merge(
        table_corresp_grade_corps, on = 'CodeEmploiGrade_neg', how = "left"
        ).rename(
            columns={"cadredemploiNETNEH":"corps_NETNEH"}
            )
    grilles_pre_ATT_w_corps = grilles_pre_ATT_w_corps.rename(columns = {'code_grade_NETNEH':'c_cir'})
    corps_impute_par_IPP = {
        "0025":"agent technique",
        "0026":"agent technique",
        "0027":"agent technique",
        "0033":"agent de salubrite",
        "0034":"agent de salubrite",
        "0035":"agent de salubrite",
        "0625":"gardien d'immeuble",
        "0626":"gardien d'immeuble",
        "0627":"gardien d'immeuble",
        "0628":"gardien d'immeuble",
        "0156":"agent de salubrite",
        "0157":"agent technique",
        "0769":"agent technique",
        "0391":"aide medico-technique qualifie"
        }
    grilles_pre_ATT_w_corps['corps_pre_2006_impute_par_IPP'] = grilles_pre_ATT_w_corps[
        'CodeEmploiGrade_neg'
        ].map(corps_impute_par_IPP)
    grade_aft_2006 = {
        "0025":"TTH3",
        "0026":"TTH2",
        "0027":"TTH1",
        "0033":"TTH3",
        "0034":"TTH2",
        "0035":"TTH1",
        "0625":"TTH1",
        "0626":"TTH2",
        "0627":"TTH3",
        "0628":"TTH4",
        "0156":"TTH4",
        "0157":"TTH4",
        "0769":"TTH1",
        "0391":"TTH1"
        }
    grilles_pre_ATT_w_corps['grade_aft_2006'] = grilles_pre_ATT_w_corps[
        'CodeEmploiGrade_neg'
        ].map(grade_aft_2006)
    grilles_pre_ATT_w_corps = grilles_pre_ATT_w_corps[[
        u'date_effet_grille',
        u'ib',
        u'echelon',
        u'max_mois',
        u'min_mois',
        u'moy_mois',
        u'libelle_FP',
        u'libelle_grade_NEG',
        u'code_grade_NEG',
        u'c_cir',
        u'corps_NETNEH', # post reforme 2006
        u'corps_pre_2006_impute_par_IPP',
        u'grade_aft_2006',
        ]]
    grilles_pre_ATT_w_corps['ib'] = grilles_pre_ATT_w_corps['ib'].astype(int)
    grilles_pre_ATT_w_corps['date_effet_grille'] = pd.to_datetime(grilles_pre_ATT_w_corps['date_effet_grille'])
    return grilles_pre_ATT_w_corps


def clean_careers_annee_annee_bef_bef_2006(data_non_chgmt_2006, data_careers, annee):
    """
    Ajoute l'ib et l'état de l'agent en 2005 au dataframe des carrières de agents qui n'ont pas changé de grade entre
    2006 et 2011. TOFIX, à fusionner avec clean_careers_annee_annee_bef_bef_2006 de clean_data_initialisation.py

    Parameters:
    ----------
    `data_non_chgmt_2006`: dataframe
    `data_careers`: dataframe
    `annee`: int

    Returns:
    ----------
    dataframe
    """
    ident_keep = data_non_chgmt_2006.ident.unique()
    data_annee = data_careers.query('annee == {}'.format(annee - 1))
    data_annee_bef = data_annee[data_annee['ident'].isin(ident_keep)][[
        'ident',
        'ib',
        'etat',
        'an_aff',
        ]].rename(columns = {'ib':'ib_{}'.format(annee), 'etat':'etat_{}'.format(annee - 1)})
    data_annee_annee_bef = data_non_chgmt_2006.merge(data_annee_bef, on = 'ident')
    return data_annee_annee_bef


def get_cas_uniques(data_annee_annee_bef):
    """
    Get cas de transitions uniques entre 2005 et 2006 (unique ib_2005 c_cir_2006)

    Parameters:
    ----------
    `data_non_chgmt_2006`: dataframe
    `data_careers`: dataframe
    `annee`: int

    Returns:
    ----------
    dataframe
    """
    cas_uniques = data_annee_annee_bef[['c_cir_2006_predit', 'ib_2005']].drop_duplicates()
    return cas_uniques


def get_grilles_en_effet_en_2005(grade_2006):
    """
    Get grilles ayant fusionné en grade_2006 en effet en 2005

    Parameters:
    ----------
    `grade_2006`: str

    Returns:
    ----------
    dataframe
    """
    grilles_pre_grade_2006 = clean_grilles_pre_ATT(
        table_corresp_grade_corps,
        grilles_pre_ATT
        ).query("grade_aft_2006 == '{}'".format(grade_2006)
        )
    uniques_grades_fusionnes_en_ce_grade_2006 = grilles_pre_grade_2006.code_grade_NEG.unique().tolist()
    dict_grades_pre_2006_et_dates_effet_grille = {}
    for grade in uniques_grades_fusionnes_en_ce_grade_2006:
        grilles_du_grade = grilles_pre_grade_2006.query("code_grade_NEG == '{}'".format(grade))
        dates_effet = grilles_du_grade.date_effet_grille
        date_effet = dates_effet[dates_effet <= pd.datetime(2005, 12, 31)].max()
        dict_grades_pre_2006_et_dates_effet_grille[grade] = date_effet
        dict_grades_pre_2006_et_dates_effet_grille[grade] = date_effet
    grades_et_dates_effet_grille = pd.DataFrame(
        dict_grades_pre_2006_et_dates_effet_grille.items(),
        columns=['code_grade_NEG', 'date_effet_grille']
        )
    grilles_completes_des_grades_de_2005 = grilles_pre_grade_2006.merge(
        grades_et_dates_effet_grille,
        on = ['code_grade_NEG', 'date_effet_grille']
        )
    return grilles_completes_des_grades_de_2005


def get_indicatrice_de_changement_de_grade_2005_2006(cas_uniques_2005_2006, grade_2006):
    """
    Impute une indicatrice de changement de grade entre l'année 2006 et l'année 2005 aux cas uniques de transition
    pour grade_2006

    - Si une personne est TTH1 en 2006, on considère qu'elle l'est déjà en 2005 si son IB de 2005 est inclu sur une des
    grilles des grades qui ont fusionné pour donner le grade TTH1 en 2006 (codes grades neg 27 35 625 ou 391) et
    qu'elle entre dans le grade des TTH1 en 2006 si son IB de 2005 n'est pas présent sur ces grilles

    - Si une personne est TTH2 TTH3 ou TTH4 en 2006, on considère qu'elle est déjà dans son grade en 2005 pour sûr si
    son IB de 2005 est inclu sur une des grilles des grades qui ont fusionné pour donner le grade de la personne en 2006
    et pas sur les grilles des grades qui ont fusionné pour donner le grade précédent (par ex. TTH1 si la pers est TTH2
    en 2006. Si l'IB est présent sur ces deux types de grilles, on dit que la situation est ambigue

    TOFIX: fusionner avec get_indicatrice_de_changement_de_grade_annee_annee_bef

    Parameters:
    ----------
    `cas_uniques_2005_2006`: dataframe
    `grade_2006` : str

    Returns:
    ----------
    dataframe
        cas uniques de transition avec une indicatrice de changement de grade pour un grade
    """
    cas_uniques = cas_uniques_2005_2006.query("c_cir_2006_predit == '{}'".format(grade_2006))
    grilles_grades_fusion_en_grade_2006 = get_grilles_en_effet_en_2005('{}'.format(grade_2006))
    grilles_grades_fusion_en_grade_precedent_grade_2006 = get_grilles_en_effet_en_2005('TTH{}'.format(int(
        grade_2006.strip()[-1]) - 1)
        )
    list_cas_uniques_w_indicatrice_chgmt_grade = []
    for cas in range(len(cas_uniques)):
        cas_unique = cas_uniques.iloc[cas]
        c_cir_2006 = str(cas_unique['c_cir_2006_predit'])
        ib_2005 = int(cas_unique['ib_2005'])
        grille_c_cir_2006_en_2005 = grilles_grades_fusion_en_grade_2006.query('ib == {}'.format(ib_2005))
        if len(grille_c_cir_2006_en_2005) == 0:
            indicatrice_chgmt_grade = 1
            ambiguite = False
            list_cas_uniques_w_indicatrice_chgmt_grade.append([c_cir_2006, ib_2005, indicatrice_chgmt_grade, ambiguite])
        else:
            if c_cir_2006 == 'TTH1':
                indicatrice_chgmt_grade = 0
                ambiguite = False
                list_cas_uniques_w_indicatrice_chgmt_grade.append(
                    [c_cir_2006, ib_2005, indicatrice_chgmt_grade, ambiguite]
                    )
            else:
                grilles_c_cir_precedent_c_cir_2006_en_2005 = grilles_grades_fusion_en_grade_precedent_grade_2006.query(
                    'ib == {}'.format(ib_2005)
                    )
                if len(grilles_c_cir_precedent_c_cir_2006_en_2005) == 0:
                    indicatrice_chgmt_grade = 1
                    ambiguite = False
                    list_cas_uniques_w_indicatrice_chgmt_grade.append(
                        [c_cir_2006, ib_2005, indicatrice_chgmt_grade, ambiguite]
                        )
                else:
                    ambiguite = True
                    list_cas_uniques_w_indicatrice_chgmt_grade.append(
                        [c_cir_2006, ib_2005, 1, ambiguite]
                        )
                    list_cas_uniques_w_indicatrice_chgmt_grade.append(
                        [c_cir_2006, ib_2005, 0, ambiguite]
                        )

        list_cas_uniques_w_indicatrice_chgmt_grade.append([c_cir_2006, ib_2005, indicatrice_chgmt_grade, ambiguite])
    cas_uniques_w_grade = pd.DataFrame(
        list_cas_uniques_w_indicatrice_chgmt_grade,
        columns = ['c_cir_2006_predit', 'ib_2005', 'indicat_ch_grade_2005', 'ambiguite_2005']
        ).drop_duplicates()
    return cas_uniques_w_grade


def merge_cas_uniques_with_grades_2005_2006(cas_uniques_w_grade):
    """
    Impute une indicatrice de changement de grade entre l'année 2006 et l'année 2005 aux cas uniques de transition

    Parameters:
    ----------

    Returns:
    ----------
    dataframe
    """
    cas_uniques_w_indicatrice_chgmt_grade = []
    for grade in ['TTH1', 'TTH2', 'TTH3', 'TTH4']:
        cas_uniques_w_indicatrice_chgmt_grade.append(
            get_indicatrice_de_changement_de_grade_2005_2006(cas_uniques_w_grade, grade)
            )
    cas_uniques_w_indic_chgmt_grade_df = pd.concat(cas_uniques_w_indicatrice_chgmt_grade)
    return cas_uniques_w_indic_chgmt_grade_df


def map_cas_uniques_2005_2006_to_data(data_2005_2006, cas_uniques_w_grade):
    """
    Impute une indicatrice de changement de grade entre l'année 2006 et l'année 2005 aux agents

    Parameters:
    ----------
    `data_2005_2006`

    Returns:
    ----------
    dataframe
    """
    cas_uniques_w_grade = merge_cas_uniques_with_grades_2005_2006(cas_uniques_w_grade)
    data_with_indicatrice_chgmt_grade_TTH1 = data_2005_2006.merge(
        cas_uniques_w_grade, on = ['ib_2005', 'c_cir_2006_predit']
        )
    return data_with_indicatrice_chgmt_grade_TTH1


table_corresp_grade_corps = pd.read_csv(
    os.path.join(grilles_path, 'corresp_neg_netneh.csv'),
    delimiter = ';'
    )
corresp_grilles_ATT_et_pre_ATT = pd.read_csv(os.path.join(grilles_path, "neg_grades_supp.csv"),
                                             delimiter = ';')

grilles_path = os.path.join(CNRACL_project_path, "assets")
grilles = pd.read_hdf(
    os.path.join(grilles_path, 'grilles_fonction_publique/grilles_old.h5')
    )
grilles = clean_grille(grilles, False, table_corresp_grade_corps)


#data_carrieres_1995_2007 = data_carrieres_1995_2015.query('(annee < 2008) & (annee > 1999)')

data_non_chgmt_2006 = pd.read_csv(
    "M:/CNRACL/output/base_AT_clean_2006_2011/data_non_changement_grade_2006_2011.csv"
    )

data_non_chgmt_2007 = pd.read_csv(
    "M:/CNRACL/output/base_AT_clean_2007_2011/data_non_changement_grade_2007_2011.csv"
    )

grilles_pre_ATT = pd.read_table(
    os.path.join(grilles_path, 'grilles_fonction_publique/neg_pour_ipp.txt')
    )


def main(results_filename):
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
    data_2005_2006 = clean_careers_annee_annee_bef_bef_2006(data_non_chgmt_2006, data_carrieres_1995_2015, 2005)
    cas_uniques = get_cas_uniques(data_2005_2006)
    cas_uniques_2005_2006_w_grade = get_indicatrice_de_changement_de_grade_2005_2006(
        cas_uniques, 'TTH1'
        )
    cas_uniques_with_indic = merge_cas_uniques_with_grades_2005_2006(cas_uniques_2005_2006_w_grade)
    data_with_indic_chgmt_2005_2006 = map_cas_uniques_2005_2006_to_data(data_2005_2006, cas_uniques_with_indic)
    get_careers_chgmt_grade_annee_annee_bef(data_with_indic_chgmt_2005_2006, False, 2006).to_csv(
        results_filename
        )

if __name__ == '__main__':
    main(os.path.join(
        os.path.join(output_directory_path, "base_AT_clean_2006_2011"),
        "data_non_changement_grade_2005_2006.csv"
        ))

