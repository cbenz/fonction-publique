# -*- coding: utf-8 -*-

"""
Date dernier edit: 23/05/2017
Auteur : Lisa Degalle

Objectif : clean_data_initialisation.py a pour but de préparer les données de carrières des adjoints techniques
territoriaux et leurs grilles en vue de l'imputation des durées déjà passées dans le grade par ces agents en 2011,
qui se fait dans le script imputations_2007_2011.py

Inputs :
    - données de carrieres des ATT de 2007 à 2015 : "corpsAT_2007.csv"
    - deux tables de grilles de la fonction publiques : "grilles_old.h5" et "neg_grades_supp.csv"
    - table de correspondance des grades et des corps : "corresp_neg_netneh.csv"

Outputs (utilisés comme inputs dans imputaion_indicatrice_chgmt_grade_annee_annee_bef imputations_2007_2011.py):
    - grilles nettoyées avec variables "corps" et année d'entrée en vigueur
    - carrières filtrées (sans ib manquant, corps des ATT en 2011, génération, code c_cir renseigné quand état activité)
    - données de carrières de l'année courante avec les variables issues des grilles
    - table des données de transitions de carrières entre année courante et année précédente
    - table des cas uniques de transitions de carrières entre année courante et année précédente

Fonctions :
    - clean_grille
    - clean_careers
    - merge_careers_with_grilles
    - clean_careers_annee_annee_bef
    - get_career_transitions_uniques_annee_annee_bef
"""

from __future__ import division
import logging
import numpy as np
import os
import pandas as pd
from fonction_publique.base import grilles_path, output_directory_path, grilles, table_corresp_grade_corps


log = logging.getLogger(__name__)

first_year = 2007

# Chemins des données de carrières :

careers_asset_path = os.path.join(
    output_directory_path,
    "select_data"
    )

# Chargement des données de carrières, des tables de grilles et de la table de correspondances des grades et des corps :
# (utile uniquement pour tester les fonctions de ce fichier indépendamment de imputations_2007_2011.py)
data_carrieres = pd.read_csv(os.path.join(careers_asset_path, "corpsAT_2007.csv"))
grilles = pd.read_hdf(os.path.join(grilles_path, 'grilles_fonction_publique/grilles_old.h5'))
grilles_supp = pd.read_csv(os.path.join(grilles_path, "neg_grades_supp.csv"), delimiter = ';')
table_corresp_grade_corps = pd.read_csv(os.path.join(grilles_path, 'corresp_neg_netneh.csv'), delimiter = ';')


def clean_grille(grilles, short, table_corresp_grade_corps):
    """
    Nettoie les grilles de la fonction publique, en modifiant les types de données, ajoutant une variable d'année
    d'entrée en vigueur de la grille (annee_effet) et ajoutant une variable spécifiant le corps d'appartenance des
    grades présents dans les grilles (corps_NETNEH)

    Parameters
    ---------
    `grilles`: dataframe
        'grilles_old.h5'
    `short`: bool
        If True, on obtient une version courte des grilles, i.e une table associant à chaque grade les dates
        d'entrée en vigueur des réformes de sa grille
        If False, on a la version complète de la grille avec les échelons, ib, etc.
    `table_corresp_grade_corps`: dataframe
        'corresp_neg_netneh.csv'

    Returns
    -------
    dataframe
        grilles courte ou longue, avec deux variables additionnelles : un corps et une année d'entrée en vigueur pour
        chaque grille
    """
    grilles['date_effet_grille'] = pd.to_datetime(grilles['date_effet_grille'])
    grilles.sort_values('date_effet_grille', inplace = True)

    grilles['c_cir'] = grilles['code_grade_NETNEH'].astype(str)
    grilles['echelon'] = grilles['echelon'].astype(str)
    grilles['annee_effet'] = (
        pd.to_datetime(
            np.array(
                grilles.date_effet_grille.astype(str),
                dtype = 'datetime64[Y]'
                )
            )
        ).year
    grilles['date_effet_grille'] = pd.to_datetime(grilles['date_effet_grille'])

    dict_corres_NETNEH = table_corresp_grade_corps.set_index('CodeNETNEH')['cadredemploiNETNEH'].to_dict()
    grilles['corps_NETNEH'] = grilles['code_grade_NETNEH'].map(dict_corres_NETNEH)

    if short:
        grilles = grilles[
            ['c_cir', 'date_effet_grille']
            ].drop_duplicates()
    else:
        grilles = grilles
    return grilles


def clean_grilles_pre_ATT(grilles_pre_ATT, short, table_corresp_grade_corps):
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
    grade_NEG_bef_769 = [32, 36, 37]
    grade_NEG_bef_26 = [30]
    grade_NEG_bef_25 = [29]
    grade_NEG_bef_TTH2 = [26, 34, 626]
    grade_NEG_bef_TTH3 = [25, 33, 627]
    grade_NEG_bef_TTH4 = [157, 156, 628]
    grades_NEG_bef_ATT = grade_NEG_bef_TTH1 + grade_NEG_bef_TTH2 + grade_NEG_bef_TTH3 + grade_NEG_bef_TTH4 + grade_NEG_bef_769 + grade_NEG_bef_26 + grade_NEG_bef_25
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
        "0391":"aide medico-technique qualifie",
        "0036":"agent d'entretien",
        "0037":"agent d'entretien",
        "0032":"conducteur",
        "0030":"conducteur",
        "0029":"garagiste",
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
        "0391":"TTH1",
        "0036":"TTH1",
        "0037":"TTH1",
        "0032":"TTH1",
        "0030":"TTH2",
        "0029":"TTH3",
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
        ]].rename(columns = {"c_cir":"c_cir_pre_2006", "grade_aft_2006":"code_grade_NETNEH"})
    grilles_pre_ATT_w_corps['ib'] = grilles_pre_ATT_w_corps['ib'].astype(int)
    grilles_pre_ATT_w_corps['date_effet_grille'] = pd.to_datetime(grilles_pre_ATT_w_corps['date_effet_grille'])
    grilles_pre_ATT_w_corps['min_mois'] = grilles_pre_ATT_w_corps['min_mois'].fillna(-1)
    grilles_pre_ATT_w_corps['max_mois'] = grilles_pre_ATT_w_corps['max_mois'].fillna(-1)
    if short:
        grilles_pre_ATT_w_corps = grilles_pre_ATT_w_corps[
            ['code_grade_NETNEH', 'date_effet_grille']
            ].drop_duplicates()
    return grilles_pre_ATT_w_corps


def get_grilles_en_effet(grade_2006, annee):
    """
    Get grilles ayant fusionné en grade_2006 en effet en 2005

    Parameters:
    ----------
    `grade_2006`: str

    Returns:
    ----------
    dataframe
    """
    grilles_pre_ATT = pd.read_table(
    os.path.join(grilles_path, 'grilles_fonction_publique/neg_pour_ipp.txt')
    )
    grilles_pre_grade_2006 = clean_grilles_pre_ATT(
        grilles_pre_ATT,
        False,
        table_corresp_grade_corps,
        ).query(
            "code_grade_NETNEH == '{}'".format(grade_2006)
            )
    uniques_grades_fusionnes_en_ce_grade_2006 = grilles_pre_grade_2006.code_grade_NEG.unique().tolist()
    dict_grades_pre_2006_et_dates_effet_grille = {}
    for grade in uniques_grades_fusionnes_en_ce_grade_2006:
        grilles_du_grade = grilles_pre_grade_2006.query("code_grade_NEG == '{}'".format(grade))
        dates_effet = grilles_du_grade.date_effet_grille
        date_effet = dates_effet[dates_effet <= pd.datetime(annee-1, 12, 31)].max()
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


def get_possible_grilles(c_cir_now, annee, grilles, table_corresp_grade_corps):
    grilles = clean_grille(grilles, False, table_corresp_grade_corps)
    date_effet_grille_bef = grilles[
        (grilles['code_grade_NETNEH'] == c_cir_now) &
        (grilles['date_effet_grille'] <= pd.datetime(annee - 1, 12, 31))
        ].date_effet_grille.max()
    # TODO: include changement de date d'effet
    if annee >= 2011:
        date_effet_grille = grilles[
            (grilles['code_grade_NETNEH'] == c_cir_now) &
            (grilles['date_effet_grille'] <= pd.datetime(annee, 12, 31))
            ].date_effet_grille.max()
        list_date_effet_grille = [date_effet_grille]
        date_effet_grille_bef = grilles[
            (grilles['code_grade_NETNEH'] == c_cir_now) &
            (grilles['date_effet_grille'] < date_effet_grille)
            ].date_effet_grille.max()
        list_date_effet_grille.append(date_effet_grille_bef)
        grille_c_cir_now = grilles[
            (grilles['code_grade_NETNEH'] == c_cir_now) &
            (grilles['date_effet_grille'].isin(list_date_effet_grille))
            ]
    elif annee == 2009:
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
    elif annee == 2007:
        grilles_fusionnees_en_c_cir_now = get_grilles_en_effet(c_cir_now, 2006)
        grilles_c_cir_2006 = grilles[
            (grilles['code_grade_NETNEH'] == c_cir_now) &
            (grilles['date_effet_grille'] == date_effet_grille_bef)
            ]
        grille_c_cir_now = grilles_fusionnees_en_c_cir_now.append(grilles_c_cir_2006)
    elif annee == 2006:
        grille_c_cir_now = get_grilles_en_effet(c_cir_now, 2006).append(
            get_grilles_en_effet(c_cir_now, 2005))
    elif annee < 2006:
        grille_c_cir_now = get_grilles_en_effet(c_cir_now, annee)
    else:
        grille_c_cir_now = grilles[
            (grilles['code_grade_NETNEH'] == c_cir_now) &
            (grilles['date_effet_grille'] == date_effet_grille_bef)
            ]
    return grille_c_cir_now


def merge_careers_with_grilles(data, grilles, annee):
    """
    Pour chaque année, entre l'année de début d'observation pour l'imputation de la durée déjà passée dans le grade
    et l'année 2011, positionne chaque agent sur une grille, en utilisant son code c_cir observé en 2011 et prédit
    pour les années précédents et l'année en cours. La grille de l'agent est celle qui correspond à son c_cir et qui
    est la dernière à être en effet l'année d'observation.

    Parameters
    ---------
    `data`: dataframe
        données de carrières
    `grilles`: dataframe
    `annee`: int
        entre 2007 et 2011, le fonctionnement est différent avant 2007 car le corps des ATT n'existait pas.

    Returns
    ---------
    dataframe
        donnée de carrière pour annee == annee avec chaque agent positionné sur une grille, et toutes les variables
        de cette grille
    """
    if annee >= 2011:
        data = data.query('annee == {}'.format(annee)).rename(columns = {"ib4": "ib"})
        data = data.rename(columns = {'echelon':'echelon_CNRACL'})
        uniques_c_cir = data.c_cir.unique().tolist()
        list_c_cir_dates_obs_effet = []
        grilles = clean_grille(grilles, False, table_corresp_grade_corps)
        grilles_short = clean_grille(grilles, True, table_corresp_grade_corps)
        for c_cir in uniques_c_cir:
            grille_short = grilles_short[
                grilles_short['c_cir'] == c_cir
                ]
            liste_dates = grille_short.date_effet_grille
            list_date_effet_grille_ant = liste_dates[liste_dates <= pd.datetime(annee, 12, 31)]
            date_effet_grille = list_date_effet_grille_ant.max()
            list_c_cir_dates_obs_effet.append([c_cir, annee, date_effet_grille])
        df_corres = pd.DataFrame(
            list_c_cir_dates_obs_effet,
            columns = ['c_cir','annee', 'date_effet_grille'],
            )
        data_with_date_effet_grille = data.merge(
            df_corres,
            on = ['c_cir', 'annee'],
            how = 'left',
            )
        data_with_info_grilles = data_with_date_effet_grille.merge(
            grilles,
            on = ['c_cir', 'ib', 'date_effet_grille'],
            how = 'left',
            )
        data_with_info_grilles = data_with_info_grilles[
            data_with_info_grilles['corps_NETNEH'] == 'adjoints techniques territoriaux'
            ]
    else:
        data_with_info_grilles = data.reset_index()
    return data_with_info_grilles


data_carrieres = pd.read_csv(os.path.join(
        output_directory_path,
        "select_data",
        "corpsAT_1995.csv"
        )).query('annee > 2001')


def get_echelon_after_2011_from_c_cir(data_carrieres,
        grades_2011 = ['TTH1', 'TTH2', 'TTH3', 'TTH4', 'STH1', 'STH2', 'STH3', 'STH4']
        ):
    grade_by_stagiaire_2011 = {
         "STH1": "TTH1",
         "STH2": "TTH2",
         "STH3":"TTH3",
         "STH4":"TTH4",
         }
    data = data_carrieres.query('annee > 2010').copy()
    # L'indice brut du dernier trimestre est gardé
    data.rename(columns = dict(ib4 = 'ib'), inplace = True)
    if grades_2011 is not None:
        idents_keep = data.query('(c_cir in @grades_2011) & (annee == 2011)').ident.unique().tolist()
        data = data.query('ident in @idents_keep')
        data = data.replace(dict(c_cir = grade_by_stagiaire_2011))

    cas_uniques_with_echelon = list()
    for annee in range(2011, 2015 + 1):
        empty_count = 0
        weight_by_cas_unique = (data
            .query('annee == @annee')
            .groupby(['c_cir', 'ib'])['ident'].count()
            )
        cas_uniques = (data
            .query('annee == @annee')[['c_cir', 'ib']]
            .drop_duplicates()
            .set_index(['c_cir', 'ib'])
            )
        for (c_cir, ib), row in cas_uniques.iterrows():

            grille_possible = (get_possible_grilles(c_cir, annee, grilles, table_corresp_grade_corps)
                .query('ib == {}'.format(ib))
                )
            if grille_possible.empty:
                echelon = -1
                min_mois = -1
                max_mois = -1
                empty_count += weight_by_cas_unique[c_cir, ib]

            else:
                if len(grille_possible) > 1:
                    date_effet_max = grille_possible.date_effet_grille.unique().max()
                    grille_possible = grille_possible.query('date_effet_grille == @date_effet_max')
                else:
                    grille_possible = grille_possible
                assert len(grille_possible) == 1

                echelon = grille_possible.echelon.values.astype(str)[0]
                min_mois = grille_possible.min_mois.values.astype(int)[0]
                max_mois = grille_possible.max_mois.values.astype(int)[0]
            cas_uniques_with_echelon.append([annee, c_cir, ib, echelon, min_mois, max_mois])

        print("annee {}, empty_count = {} for {} cas_unique ({} %)".format(
            annee,
            empty_count,
            len(data.query('annee == @annee').ident.unique()),
            100 * empty_count/len(data.query('annee == @annee').ident.unique())
            ))
    #
    cas_uniques = pd.DataFrame(
        cas_uniques_with_echelon,
        columns = ['annee', 'c_cir', 'ib', 'echelon', 'min_mois', 'max_mois'],
        )
    cas_uniques['echelon'] = cas_uniques['echelon'].replace({'ES':55555}).astype(int)
    assert not cas_uniques[['c_cir', 'ib', 'annee']].duplicated().any()
    data = data.merge(cas_uniques, on = ['c_cir', 'ib', 'annee'])
    return data[
        ['ident',  'annee', 'c_cir', 'statut', 'ib', 'echelon4', 'etat4', 'generation',
            'sexe', 'an_aff', 'echelon', 'min_mois', 'max_mois']
        ].rename(columns = dict(echelon4 = 'echelon_CNRACL', etat4 = 'etat'))


def clean_careers(data, corps, ib_manquant_a_exclure, generation_min, grilles):
    """
    Retourne une table des carrières entre 2003 et 2015 des agents qui sont:
        sont ATT en 2011 selon leur c_cir, y compris les stagiaires
        sont d'une génération supérieure à generation_min
        n'ont pas d'IB manquant sur la période
        n'ont pas de code cir nul quand leur état est en activité après 2010
        sont rattachés à une grille en 2011

    Parameters
    ---------
    `data`: dataframe
        données de carrières (data_carrieres)
    `corps`: str
        'ATT' (TOFIX, à l'avenir on voudrait pouvoir avoir tous les corps en argument)
    `ib_manquant_a_exclure`: bool
        if True, on supprime les carrières des agents qui ont un IB manquant (= -1) sur la
        période d'observation, ici 2003 à 1015
    `generation_min`: int
        permet de ne pas sélectionner les carrières des agents les plus âgés si on ne veut pas gérer
        des fins de grade qui sont en fait des passage à la retraite

    Returns
    ---------
    dataframe
        Les données de carrières filtrées selon la description
        Un print d'une table LaTeX qui permet de suivre les pertes associées à chaque filtre
    """
    tracking = []
    tracking.append(['Aucun', len(data.ident.unique())])
    if corps == "ATT":
        'on ne garde que les agents qui sont ATT en 2011, y compris les stagiaires des ATT (STH1, STH2 etc.)'
        ident_keep_in_corps_2011 = data[(
            data['annee'] == 2011) & (data['c_cir'].isin(
                ['TTH1', 'TTH2', 'TTH3', 'TTH4', 'STH1', 'STH2', 'STH3', 'STH4']
                )
            )].ident.unique()
        data = data[data['ident'].isin(ident_keep_in_corps_2011)]
        tracking.append(['Corps des {} en 2011'.format('ATT'), len(data.ident.unique())])
    data.c_cir = data.c_cir.replace({
         "STH1": "TTH1",
         "STH2": "TTH2",
         "STH3":"TTH3",
         "STH4":"TTH4",
         })
    data = data[['ident', 'an_aff', 'annee', 'c_cir', 'sexe', 'ib4', 'echelon4', 'generation', 'etat4']].rename(
        columns = {"ib4": "ib", "etat4": "etat", "echelon4": "echelon"}
        )
    data = data.query('generation > {}'.format(generation_min))
    tracking.append([r'Génération > {}'.format(generation_min), len(data.ident.unique())])
    data_2011_2015 = data[data['annee'] > 2010]
    ident_del_c_cir_nul_etat_activite_apres_2010 = data_2011_2015[
        data_2011_2015['c_cir'].isnull() & data_2011_2015['etat'] == 1
        ].ident.unique()
    data = data[~data['ident'].isin(ident_del_c_cir_nul_etat_activite_apres_2010)]
    tracking.append([r'Code cir nul et état activité après 2010', len(data.ident.unique())])
    if ib_manquant_a_exclure:
        ident_to_del = data.query('ib == -1').ident.unique()
        data = data[~data['ident'].isin(ident_to_del)]
        tracking.append([r'IB manquant entre 2003 et 2015', len(data.ident.unique())])
    idents_to_keep_on_grilles_in_2011 = merge_careers_with_grilles(data, grilles, 2011).ident.unique()
    data = data[data['ident'].isin(idents_to_keep_on_grilles_in_2011)]
    tracking.append([r'Rattaché à une grille en 2011', len(data.ident.unique())])
    # data pas de retour
    data_c_cir_2011 = data.query('annee == 2011')[['ident', 'c_cir']].rename(
        columns = {'c_cir':'c_cir_2011'})
    data = data.merge(data_c_cir_2011, on = 'ident', how = 'outer')
    data_c_cir_diff_2011_aft_2011 = data.query('(annee > 2010) & (c_cir != c_cir_2011)')[['ident','annee']].rename(
        columns = {'annee':'annee_c_cir_diff_c_cir_2011'})
    data_merge = data.merge(data_c_cir_diff_2011_aft_2011, on ='ident', how ='outer')
    data_merge['annee_c_cir_diff_c_cir_2011'] = data_merge['annee_c_cir_diff_c_cir_2011'].fillna(5000)
    ident_to_del = data_merge.query(
        '(annee > 2010) & (annee > annee_c_cir_diff_c_cir_2011) & (c_cir == c_cir_2011)').ident.unique()
    print ident_to_del
    data = data[~data['ident'].isin(ident_to_del)]
    tracking.append([r'Sans sortie/retour du grade de 2011', len(data.ident.unique())])
    tracking = pd.DataFrame(tracking)
    print tracking.to_latex()
    return data


def clean_careers_annee_annee_bef(data_annee, data, annee, corps):
    '''
    Ajoute les informations de carrières à année moins un aux données de carrières d'une année, comme nouvelles var

    Parameters
    ---------
    `data_annee`: dataframe
        données de carrière de l'année en cours si annee différent de 2011, sinon données de carrières de 2011
    `data`: dataframe
        données de carrière
    `annee`: int
        année en cours
    `corps`: str
        'ATT'

    Returns
    ---------
        Une table des carrières avec les informations des grilles pour l'année en cours et les informations de carrières
        pour l'année précédente
    '''
    if annee == 2011:
        data_annee = data_annee.query("(corps_NETNEH == '{}') & (annee == 2011)".format(corps))
    else:
        data_annee = data_annee

    data_annee = data_annee.rename(
        columns = {
            'c_cir': 'c_cir_now',
#            'date_effet_grille': 'date_effet_grille_now',
            }
        )
    idents_keep = data_annee.ident.unique().tolist()
    data_annee_bef = data.query('annee == {}'.format(annee - 1))
    data_annee_bef = data_annee_bef[data_annee_bef['ident'].isin(idents_keep)]
    data_annee_bef = data_annee_bef.rename(
        columns = {
            "ib4": "ib_bef",
            }
        )

    data_annee_bef = data_annee_bef[['ident', 'ib_bef']]

    data_annee = data_annee[[
        'ident',
        'annee',
        'c_cir_now',
#            'date_effet_grille_now',
        'corps_NETNEH'
        ]]

    merged = data_annee.merge(data_annee_bef, on = 'ident', how = 'inner')
    merged.rename(columns = {"c_cir_now": "c_cir"}, inplace = True)
    merged.set_index(['ident', 'ib_bef', 'c_cir'], inplace = True)
    return merged


def get_career_transitions_uniques_annee_annee_bef(data_annee_annee_bef, annee):
    """
    Retourne les cas uniques de transitions de carrières entre l'année en cours et l'année précédente, définis
    comme un unique couple code cir de l'année en cours et indice brut de l'année précédente

    Parameters
    ---------
    `data_annee_annee_bef`: dataframe
        données de carrières de l'année en cours et de l'année précédente (output de clean_careers_annee_annee_bef)
    `annee`: int
        année en cours

    Returns
    ---------
    dataframe
        cas uniques de transitions de carrières
    """
    cas_uniques = (data_annee_annee_bef
        .reset_index()[["c_cir", "ib_bef", "annee",]] #"date_effet_grille_now"]]
        .drop_duplicates()
        .set_index(["annee", "ib_bef", "c_cir"])
        )
    return cas_uniques


def get_careers_chgmt_grade_annee_annee_bef(data_with_indicatrice_grade_change, get_data_for_annee_bef, annee):
    """
    Retourne les données des agents qui changent de grades entre année courante et année précédente

    Parameters
    ---------
    `data_with_indicatrice_grade_change` dataframe
        données de carrières de l'année et l'année précédente avec une indicatrice de changement de grade et un statut
        d'ambiguité
    `chgmt_grade` bool
        if True, sélectionne les agents qui changent de grade entre année et année précédente
        if False, sélectionne les agents qui ne changent pas de grade entre année et année précédente
    `stock` bool
        if True, garde toutes les variables
        if False et chgmt_grade == False, garde uniquement les variables nécessaires à voir si l'agent a changé
        de grade la période précédente
    `annee` int
        année courante
    Returns
    ---------
    dataframe
        table des carrières des agents pour l'année et l'année précédente des agents qui changent ou ne changent pas de
        grade entre l'année et l'année précédente
    """
    if get_data_for_annee_bef:
        data_with_indicatrice_grade_change = data_with_indicatrice_grade_change.query('indicat_ch_grade == False')
        data_with_indicatrice_grade_change = data_with_indicatrice_grade_change[[
            'date_effet_grille',
            'corps_NETNEH',
            ]].reset_index()
        data_with_indicatrice_grade_change = data_with_indicatrice_grade_change[[
            'ident', 'c_cir', 'ib_bef', 'date_effet_grille', 'corps_NETNEH'
            ]].rename(columns = {'ib_bef':'ib'})
        data_with_indicatrice_grade_change['annee'] = annee - 1
    else:
        data_with_indicatrice_grade_change = data_with_indicatrice_grade_change
        #.query('indicat_ch_grade != False')
    return data_with_indicatrice_grade_change

