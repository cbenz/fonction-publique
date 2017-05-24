# -*- coding: utf-8 -*-
"""
Date dernier edit: 23/05/2017
Auteur : Lisa Degalle

Objectif : imputation_indicatrice_chgmt_grade_annee_annee_bef.py a pour but d'attribuer à chaque transitions uniques
de carrières entre l'année courante et l'année précédente (un couple unique code cir année courante - indice brut de
l'année précédente) une indicatrice de changement de grade entre l'année courante et l'année précédente, et un degré
de certitude sur cette indicatrice

Inputs :
    - cas uniques de transitions de carrières (output de get_career_transitions_uniques_annee_annee_bef)
    - inputs requis par clean_data_initialisation.py

Outputs (utilisés comme inputs dans imputations_2007_2011.py):
    - cas uniques de transitions de carrières avec une indicatrice de changement de grade et un degré de certitude
    (TOFIX: appelé statut d'ambiguité)
    - données de carrières avec une indicatrice de chgmt de grade et un statut d'ambiguité pour année courante et année
    précédente

Fonctions :
    - get_indicatrice_chgmt_grade_annee_annee_bef
    - map_transitions_uniques_annee_annee_bef_to_data
"""

from __future__ import division
import numpy as np
import os
import pandas as pd
from clean_data_initialisation import (
    merge_careers_with_grilles,
    clean_careers_annee_annee_bef,
    get_career_transitions_uniques_annee_annee_bef,
    clean_grille,
    )

def get_indicatrice_chgmt_grade_annee_annee_bef(
    data_cas_uniques,
    transit_intra_corps,
    annee,
    grilles,
    table_corresp_grade_corps
    ):
    """
    Attribue à chaque cas de transition unique (couple unique de c_cir de l'année en cours et d'ib de l'année
    précédente) une indicatrice de changement de grade et un statut d'ambiguité.

    Pour ce faire, on regarde si l'ib de l'année précédente est présent sur la grille en cours à l'année précédente
    du c_cir de l'année en cours.
        - Si l'ib n'y est pas, on déduit que le cas est un cas de changement de grade, on
        attribue une indicatrice de changement de grade et un statut d'ambiguité 'non ambigu'
        - Si l'ib est sur cette grille et pas sur une autre grille du même corps, l'indicatrice de changement de grade
        vaut 0 et le statut d'ambiguité est 'non ambigu'
        - Si l'ib est sur cette grille et sur la grille du grade précédent le grade/c_cir de l'année courante, on
        duplique le cas de transition et associe aux deux cas deux indicatrices différentes de changement de grade et
        un statut d'ambiguité est 'ambigu'. (TOFIX)

    Pour la transition 2008 et 2009, on prend en compte un retard dans l'application de la réforme des grilles des
    carrières des ATT en regardant si l'ib 2008 est présent sur les grilles du c_cir 2009 en effet en 2007 ou en 2008.

    Parameters:
    ----------
    `data_cas_uniques` dataframe
        output de get_career_transitions_uniques_annee_annee_bef
    `transit_intra_corps` bool (useless pour l'instant)
        True, on vérifie que l'ib est présent sur les grilles du grade de l'année courante ou du grade précédent ce
        grade dans la hiérarchie des grades du corps
    `annee` int
        annee courante
    `grilles` dataframe
        'grilles_old.h5'
    `table_corresp_grade_corps` TOFIX

    Returns:
    ----------
    dataframe
        cas uniques avec indicatrice de changement de grade et statut d'ambiguité comme nouvelles var

    """
    cas_uniques = data_cas_uniques
    cas_uniques_with_indic_chgmt_grade = []
    for cas in range(len(cas_uniques)):
        cas_unique = cas_uniques.iloc[cas]
        c_cir_now = str(cas_unique['c_cir_{}'.format(annee)])
        date_effet_grille_now = pd.to_datetime(cas_unique['date_effet_grille_{}'.format(annee)])
        ib_bef = int(cas_unique['ib_{}'.format(annee - 1)])
        grilles = clean_grille(grilles, False, table_corresp_grade_corps)
        date_effet_grille_bef = grilles[
            (grilles['code_grade_NETNEH'] == c_cir_now) &
            (grilles['date_effet_grille'] <= pd.datetime(annee - 1, 12, 31))
            ].date_effet_grille.max()
        if annee == 2009:
            list_date_effet_grille_bef = [date_effet_grille_bef]
            date_effet_grille_bef_precedente = grilles[
                (grilles['code_grade_NETNEH'] == c_cir_now) &
                (grilles['date_effet_grille'] < date_effet_grille_bef)
                ].date_effet_grille.max()
            list_date_effet_grille_bef.append(date_effet_grille_bef_precedente)
            grille_c_cir_now = grilles[
                (grilles['code_grade_NETNEH'] == c_cir_now) &
                (grilles['date_effet_grille'].isin(list_date_effet_grille_bef))
                ]
        else:
            grille_c_cir_now = grilles[
                (grilles['code_grade_NETNEH'] == c_cir_now) &
                (grilles['date_effet_grille'] == date_effet_grille_bef)
                ]
        grille_c_cir_now_inter_ib_bef = grille_c_cir_now.query(
            'ib == {}'.format(ib_bef)
            )
        if len(grille_c_cir_now_inter_ib_bef) == 0:
            cas_uniques_with_indic_chgmt_grade.append(
                pd.DataFrame([
                    c_cir_now,
                    ib_bef,
                    date_effet_grille_now,
                    "autre_grade_que_grade_suivant",
                    1,
                    1,
                    False,
                    True
                    ]).transpose().rename(
                        columns = {
                            0: "c_cir_{}".format(annee),
                            1: "ib_{}".format(annee - 1),
                            2: "date_effet_grille_{}".format(annee),
                            3: "c_cir_{}_predit".format(annee - 1),
                            4: "rang_grade_possible_{}".format(annee - 1),
                            5: "nombre_de_grades_possibles_{}".format(annee - 1),
                            6: "ambiguite_{}".format(annee - 1),
                            7: "indicat_ch_grade_{}".format(annee - 1)
                            }
                        )
            )
        elif ib_bef in([0, 'NaN', -1]):
            cas_uniques_with_indic_chgmt_grade.append(
                pd.DataFrame([
                    c_cir_now,
                    ib_bef,
                    date_effet_grille_now,
                    "autre_grade_que_grade_suivant_ib_in_non_informatif",
                    1,
                    1,
                    False,
                    True
                    ]).transpose().rename(
                        columns = {
                            0: "c_cir_{}".format(annee),
                            1: "ib_{}".format(annee - 1),
                            2: "date_effet_grille_{}".format(annee),
                            3: "c_cir_{}_predit".format(annee - 1),
                            4: "rang_grade_possible_{}".format(annee - 1),
                            5: "nombre_de_grades_possibles_{}".format(annee - 1),
                            6: "ambiguite_{}".format(annee - 1),
                            7: "indicat_ch_grade_{}".format(annee - 1)
                            }
                        )
                )
        else:
            if transit_intra_corps:
                corps_now = grille_c_cir_now['corps_NETNEH'].unique()
                grilles['annee_effet'] = (pd.to_datetime(np.array(
                    grilles.date_effet_grille.astype(str), dtype='datetime64[Y]'
                    ))).year
                if annee == 2009:
                    grilles_corps = grilles.query("corps_NETNEH == {}".format(corps_now, annee - 1))
                    list_dates_effet = ['2008-01-07', '2006-01-11']
                    grilles_possibles = grilles_corps[grilles_corps['date_effet_grille'].isin(list_dates_effet)]
                else:
                    grilles_corps = grilles.query(
                        "(corps_NETNEH == {}) & (annee_effet <= {})".format(corps_now, annee - 1)
                        )
                    df_dates_effet_max_par_grade = grilles_corps.groupby(
                        'code_grade_NETNEH'
                        )['date_effet_grille'].max().reset_index()
                    grilles_possibles = df_dates_effet_max_par_grade.merge(
                        grilles_corps,
                        on = ['code_grade_NETNEH', 'date_effet_grille'],
                        how = 'left',
                        )
                grades_possibles_bef = grilles_possibles.query(
                    'ib == {}'.format(ib_bef)
                    )[
                        ['code_grade_NETNEH', 'code_grade_NEG', 'date_effet_grille']
                        ].rename(columns = {
                            "code_grade_NETNEH": "c_cir_{}_predit".format(annee - 1),
                            "code_grade_NEG": "c_neg_{}_predit".format(annee - 1),
                            "date_effet_grille": "date_effet_grille_{}".format(annee - 1)
                            }
                        )
                grades_possibles_bef["c_cir_{}".format(annee)] = [c_cir_now] * len(grades_possibles_bef)
                grades_possibles_bef["ib_{}".format(annee - 1)] = [ib_bef] * len(grades_possibles_bef)
                grades_possibles_bef[
                    "date_effet_grille_{}".format(annee)
                    ] = [date_effet_grille_now] * len(grades_possibles_bef)
                grades_possibles_bef["indicat_ch_grade_{}".format(annee - 1)] = (
                    grades_possibles_bef["c_cir_{}".format(annee)] !=
                    grades_possibles_bef["c_cir_{}_predit".format(annee - 1)]
                    )
                c_neg_now = int(grades_possibles_bef.query(
                    'indicat_ch_grade_{} == False'.format(annee - 1)
                    )['c_neg_{}_predit'.format(annee - 1)].unique()
                    )
                grades_possibles_bef = grades_possibles_bef.query(
                    'c_neg_{}_predit <= {}'.format(annee - 1, c_neg_now)
                    )
                grades_possibles_bef = grades_possibles_bef.query(
                    'c_neg_{}_predit > {}'.format(annee - 1, c_neg_now - 2)
                    )
                grades_possibles_bef['nombre_de_grades_possibles_{}'.format((annee - 1))] = len(grades_possibles_bef)
                grades_possibles_bef['rang_grade_possible_{}'.format(annee - 1)] = range(
                    1,
                    len(grades_possibles_bef) + 1
                    )
                grades_possibles_bef["ambiguite_{}".format(annee - 1)] = (
                    len(grades_possibles_bef['indicat_ch_grade_{}'.format(annee - 1)].value_counts()) != 1
                    )
                grades_possibles_bef = grades_possibles_bef.drop_duplicates(
                    grades_possibles_bef.columns.difference(['date_effet_grille_{}'.format(annee - 1)])
                    )
                cas_uniques_with_indic_chgmt_grade.append(grades_possibles_bef)
            else:
                stop # TOFIX, pour admettre dans l'ensemble des grilles possibles les grilles extérieures au corps
    cas_uniques_w_indic_df = pd.concat(cas_uniques_with_indic_chgmt_grade)
    return cas_uniques_w_indic_df


def map_transitions_uniques_annee_annee_bef_to_data(cas_uniques_w_indic_df, data, annee):
    """
    On assigne à chaque individu pour l'année précédent l'année courante une indicatrice de s'il a changé de grade
    ou non entre l'année précédente et l'année courante, ainsi qu'un statut d'ambiguité pour cette indicatrice.

    Parameters:
    ----------
    `cas_uniques_w_indic_df` dataframe
        données des transitions uniques de carrières avec indicatrice de changement de grade
        (output de get_indicatrice_chgmt_grade_annee_annee_bef)
    `data` dataframe
        donnees de carrieres pour l'année courante et l'année précédente (output de clean_careers_annee_annee_bef)
    `annee` int
        annee courante

    Returns:
    ----------
    dataframe
    """
    cas_uniques = cas_uniques_w_indic_df
    data = data
    data_with_indicatrice_grade_change = data.merge(
        cas_uniques,
        how = 'outer',
        on = ['c_cir_{}'.format(annee),
        'ib_{}'.format(annee - 1)]
        )
    data_with_indicatrice_grade_change = data_with_indicatrice_grade_change[[
        'ident',
        'c_cir_{}'.format(annee),
        'ib_{}'.format(annee),
        'date_effet_grille_{}_x'.format(annee),
        'date_effet_grille_{}'.format(annee - 1),
        'ib_{}'.format(annee - 1),
        'ambiguite_{}'.format(annee - 1),
        'c_cir_{}_predit'.format(annee - 1),
        'indicat_ch_grade_{}'.format(annee - 1),
        'nombre_de_grades_possibles_{}'.format(annee - 1),
        'rang_grade_possible_{}'.format(annee - 1),
        ]]
    data_with_indicatrice_grade_change = data_with_indicatrice_grade_change.rename(
        columns = {
            "date_effet_grille_{}_x".format(annee): "date_effet_grille_{}".format(annee)
            }
        )
    return data_with_indicatrice_grade_change


