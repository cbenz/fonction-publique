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
import os
import pandas as pd
from clean_data_initialisation import (
    merge_careers_with_grilles,
    clean_careers_annee_annee_bef,
    get_career_transitions_uniques_annee_annee_bef,
    clean_grille,
    clean_careers,
    clean_grilles_pre_ATT,
    get_grilles_en_effet,
    get_possible_grilles,
    )
from fonction_publique.base import (
    asset_path,
    grilles_path,
    output_directory_path,
    table_corresp_grade_corps,
    grilles
    )


def format_output(
        c_cir_now,
        ib_bef,
        c_cir_bef_predit,
        nombre_de_grades_possibles_before,
        ambiguite_before,
        indicat_ch_grade_before,
        annee,
        echelon,
        min_mois,
        max_mois,
        date_effet_grille,
        corps):

    df = pd.DataFrame({
        "ib_bef": [ib_bef],
        "c_cir": [c_cir_now],
        "c_cir_bef_predit": [c_cir_bef_predit],
        "nombre_de_grades_possibles": [nombre_de_grades_possibles_before],
        "ambiguite": [ambiguite_before],
        "indicat_ch_grade": [indicat_ch_grade_before],
        "annee": [annee],
        "echelon":[echelon],
        "min_mois":[min_mois],
        "max_mois":[max_mois],
        "date_effet_grille":[date_effet_grille],
        "corps_NETNEH":[corps]
        }).set_index(["annee", "ib_bef", "c_cir"])

    return df


corresp_grilles_ATT_et_pre_ATT = pd.read_csv(os.path.join(grilles_path, "neg_grades_supp.csv"),
                                             delimiter = ';')
grilles_pre_ATT = pd.read_table(
    os.path.join(grilles_path, 'grilles_fonction_publique/neg_pour_ipp.txt')
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
    cas_uniques_with_indic_chgmt_grade = []
    for annee_, ib_bef, c_cir in data_cas_uniques.index:
        assert annee_ == annee
        # TODO: Loop over transition = (ib_bef, c_cir_now, annee)  annee = annee finale
        c_cir_now = str(c_cir)
        c_cir_now_lower = 'TTH{}'.format(int(c_cir_now[-1:]) - 1)
        ib_bef = int(ib_bef)
        grille_c_cir_now = get_possible_grilles(c_cir_now, annee, grilles, table_corresp_grade_corps)
        assert ib_bef not in(['NaN', -1])
        grille_c_cir_now_inter_ib_bef = grille_c_cir_now.query('ib == {}'.format(ib_bef))

        # Changement de grade sur
        if len(grille_c_cir_now_inter_ib_bef) == 0:
            if c_cir_now == 'TTH1':
                cas_uniques_with_indic_chgmt_grade.append(format_output(
                    c_cir_now = c_cir_now,
                    ib_bef = ib_bef,
                    c_cir_bef_predit = "autre",
                    nombre_de_grades_possibles_before = 1,
                    ambiguite_before = False,
                    indicat_ch_grade_before = True,
                    annee = annee,
                    echelon = None,
                    min_mois = None,
                    max_mois = None,
                    date_effet_grille = None,
                    corps = None,
                    ))
            else:
                grille_c_cir_now_lower = get_possible_grilles(
                    c_cir_now_lower,
                    annee,
                    grilles,
                    table_corresp_grade_corps,
                    ).query(
                        'ib == {}'.format(ib_bef)
                        )[[
                        'code_grade_NETNEH',
                        'date_effet_grille',
                        'echelon',
                        'min_mois',
                        'max_mois',
                        'moy_mois',
                        'corps_NETNEH',
                        ]]
                if len(grille_c_cir_now_lower) == 0:
                    cas_uniques_with_indic_chgmt_grade.append(format_output(
                        c_cir_now = c_cir_now,
                        ib_bef = ib_bef,
                        c_cir_bef_predit = "autre",
                        nombre_de_grades_possibles_before = 1,
                        ambiguite_before = False,
                        indicat_ch_grade_before = True,
                        annee = annee,
                        echelon = None,
                        min_mois = None,
                        max_mois = None,
                        date_effet_grille = None,
                        corps = None,
                        ))
                else:
                    date_effet_grille_max = grille_c_cir_now_lower.date_effet_grille.unique().max()
                    grille_c_cir_now_lower = grille_c_cir_now_lower.query(
                        'date_effet_grille == @date_effet_grille_max'
                        )
                    cas_uniques_with_indic_chgmt_grade.append(format_output(
                        c_cir_now = c_cir_now,
                        ib_bef = ib_bef,
                        c_cir_bef_predit = c_cir_now_lower,
                        nombre_de_grades_possibles_before = 1,
                        ambiguite_before = False,
                        indicat_ch_grade_before = True,
                        annee = annee,
                        echelon = grille_c_cir_now_lower['echelon'].values.astype(int)[0],
                        min_mois = grille_c_cir_now_lower['min_mois'].values.astype(int)[0],
                        max_mois = grille_c_cir_now_lower['max_mois'].values.astype(int)[0],
                        date_effet_grille = grille_c_cir_now_lower['date_effet_grille'].values[0],
                        corps = grille_c_cir_now_lower['corps_NETNEH'].values.astype(str)[0],
                        ))

        else:
            if transit_intra_corps:
                if c_cir_now != 'TTH1':
                    grille_c_cir_now_lower = get_possible_grilles(
                        c_cir_now_lower,
                        annee,
                        grilles,
                        table_corresp_grade_corps,
                        )
                    grades_possibles_bef = grille_c_cir_now_lower.query(
                        'ib == {}'.format(ib_bef)
                        )[[
                        'code_grade_NETNEH',
                        'date_effet_grille',
                        'echelon',
                        'min_mois',
                        'max_mois',
                        'moy_mois',
                        'corps_NETNEH',
                        ]]
                    if len(grades_possibles_bef) != 0:
                        grades_possibles = grades_possibles_bef.append(
                            pd.DataFrame([c_cir_now,
                             grille_c_cir_now_inter_ib_bef['date_effet_grille'].values[0],
                             grille_c_cir_now_inter_ib_bef['echelon'].values.astype(str)[0],
                             grille_c_cir_now_inter_ib_bef['min_mois'].values.astype(int)[0],
                             grille_c_cir_now_inter_ib_bef['max_mois'].values.astype(int)[0],
                             grille_c_cir_now_inter_ib_bef['moy_mois'].values.astype(int)[0],
                             grille_c_cir_now_inter_ib_bef['corps_NETNEH'].values.astype(str)[0],
                             ]).transpose().rename(
                                columns = {
                                    0:'code_grade_NETNEH',
                                    1:'date_effet_grille',
                                    2:'echelon',
                                    3:'min_mois',
                                    4:'max_mois',
                                    5:'moy_mois',
                                    6:'corps_NETNEH',
                                    }))
                        rang_grade_possible = 1
                        for index, row in grades_possibles.iterrows():
                            rang_grade_possible +=1
                            cas_uniques_with_indic_chgmt_grade.append(format_output(
                                c_cir_now = c_cir_now,
                                ib_bef = ib_bef,
                                c_cir_bef_predit = row["code_grade_NETNEH"],
                                nombre_de_grades_possibles_before = len(grades_possibles.code_grade_NETNEH.unique()),
                                indicat_ch_grade_before = row["code_grade_NETNEH"] != c_cir_now,
                                ambiguite_before = len(grades_possibles) != 1,
                                annee = annee,
                                echelon = row["echelon"],
                                min_mois = row["min_mois"],
                                max_mois = row["max_mois"],
                                date_effet_grille = row["date_effet_grille"],
                                corps = row["corps_NETNEH"]
                                ))

                    else:
                        cas_uniques_with_indic_chgmt_grade.append(format_output(
                            c_cir_now = c_cir_now,
                            ib_bef = ib_bef,
                            c_cir_bef_predit = c_cir_now,
                            nombre_de_grades_possibles_before = 1,
                            indicat_ch_grade_before = False,
                            ambiguite_before = False,
                            annee = annee,
                            echelon = grille_c_cir_now_inter_ib_bef["echelon"].values.astype(str)[0],
                            min_mois = grille_c_cir_now_inter_ib_bef["min_mois"].values.astype(int)[0],
                            max_mois = grille_c_cir_now_inter_ib_bef["max_mois"].values.astype(int)[0],
                            date_effet_grille = grille_c_cir_now_inter_ib_bef["date_effet_grille"].values[0],
                            corps = grille_c_cir_now_inter_ib_bef["corps_NETNEH"].values.astype(str)[0]
                            ))
                else:
                    grades_possibles_bef = None
                    rang_grade_possible = 1
                    for index, row in grille_c_cir_now_inter_ib_bef.iterrows():
                        cas_uniques_with_indic_chgmt_grade.append(format_output(
                            c_cir_now = c_cir_now,
                            ib_bef = ib_bef,
                            c_cir_bef_predit = c_cir_now,
                            nombre_de_grades_possibles_before = 1,
                            indicat_ch_grade_before = False,
                            ambiguite_before = False,
                            annee = annee,
                            echelon = row["echelon"],
                            min_mois = row["min_mois"],
                            max_mois = row["max_mois"],
                            date_effet_grille = row["date_effet_grille"],
                            corps = row["corps_NETNEH"]
                            ))
            else:
                # FIXME pour admettre dans l'ensemble des grilles possibles les grilles extérieures au corps
                raise(NotImplementedError)

    cas_uniques_w_indic_df = pd.concat(cas_uniques_with_indic_chgmt_grade)

    assert (cas_uniques_w_indic_df.query('ambiguite').groupby(
        ['annee', 'ib_bef', 'c_cir']
        )['c_cir_bef_predit'].count() > 1).all()
    assert (cas_uniques_w_indic_df.query("(not(ambiguite)) & (c_cir != 'TTH1')").groupby(
        ['annee', 'ib_bef', 'c_cir']
        )['c_cir_bef_predit'].count() == 1).all()

    c_cir_bef_predits = (cas_uniques_w_indic_df.query(
            '(indicat_ch_grade == True) & (ambiguite == False)').c_cir_bef_predit
            .value_counts(dropna = False)
            .index.tolist()
            )
    assert 'TTH1' in c_cir_bef_predits
    return cas_uniques_w_indic_df


def map_transitions_uniques_annee_annee_bef_to_data(cas_uniques_with_indic_grade_change, data, annee):
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
    cas_uniques_with_indic_grade_change = cas_uniques_with_indic_grade_change.reset_index()
    data = data.reset_index()
    data_with_indicatrice_grade_change = data.merge(
        cas_uniques_with_indic_grade_change, how = 'outer', on = ['c_cir', 'ib_bef', 'annee']
        )
    data_with_indicatrice_grade_change = data_with_indicatrice_grade_change.set_index(
        ['ident', 'annee', 'c_cir', 'ib_bef']
        ).rename(columns = {'corps_NETNEH_x':'corps_NETNEH'})
    return data_with_indicatrice_grade_change


