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
    - clean_data_carriere_initial
    - merge_careers_with_grilles
    - clean_careers_annee_annee_bef
    - get_career_transitions_uniques_annee_annee_bef
"""

from __future__ import division
import logging
import numpy as np
import os
import pandas as pd
from fonction_publique.base import grilles_path, output_directory_path

log = logging.getLogger(__name__)

# Chemins des données de carrières :
careers_asset_path = os.path.join(
    output_directory_path,
    "bases_AT_imputations_trajectoires_avant_2011"
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
    if annee == 2011:
        data = data.query('annee == {}'.format(annee)).rename(columns = {"ib4": "ib"})
    else:
        data = data
        data["annee"] = annee
    grilles = clean_grille(grilles, False, table_corresp_grade_corps)
    grilles_short = clean_grille(grilles, True, table_corresp_grade_corps)
    if annee == 2011:
        uniques_data_points = data[[
            "annee", "c_cir"
            ]].drop_duplicates()
        uniques_c_cir = uniques_data_points.c_cir.unique().tolist()
    else:
        uniques_data_points = data[[
            "annee",
            "c_cir_{}_predit".format(annee)
            ]]
        uniques_c_cir = uniques_data_points['c_cir_{}_predit'.format(annee)].unique().tolist()
    list_c_cir_dates_obs_effet = []
    for c_cir in uniques_c_cir:
        grille_short = grilles_short[
            grilles_short['c_cir'] == c_cir
            ]
        liste_dates = grille_short.date_effet_grille
        list_date_effet_grille_ant = liste_dates[liste_dates <= pd.datetime(annee, 12, 31)]
        date_effet_grille = list_date_effet_grille_ant.max()
        list_c_cir_dates_obs_effet.append([c_cir, annee, date_effet_grille])
    if annee == 2011:
        df_corres = pd.DataFrame(
            list_c_cir_dates_obs_effet,
            columns = ['c_cir', 'annee', 'date_effet_grille'],
            )
        data_with_date_effet_grille = data.merge(
            df_corres,
            on = ['c_cir', 'annee'],
            how = 'left',
            )
        data_with_info_grilles = data_with_date_effet_grille.merge(
            grilles,
            on = ['date_effet_grille', 'c_cir', 'ib'],
            how = 'left',
            )
        data_with_info_grilles = data_with_info_grilles[
            ~data_with_info_grilles[
                'date_effet_grille'
                ].isnull()
            ]
    else:
        df_corres = pd.DataFrame(
            list_c_cir_dates_obs_effet,
            columns = ['c_cir_{}_predit'.format(annee),'annee', 'date_effet_grille_{}'.format(annee)],
            )
        data_with_date_effet_grille = data.merge(
            df_corres,
            on = ['c_cir_{}_predit'.format(annee), 'annee', 'date_effet_grille_{}'.format(annee)],
            how = 'left',
            )
        grilles['c_cir_{}_predit'.format(annee)] = grilles['c_cir']
        grilles['date_effet_grille_{}'.format(annee)] = grilles['date_effet_grille']
        grilles['ib_{}'.format(annee)] = grilles['ib']
        data_with_info_grilles = data_with_date_effet_grille.merge(
            grilles,
            on = [
                'date_effet_grille_{}'.format(annee),
                'c_cir_{}_predit'.format(annee),
                'ib_{}'.format(annee)
                ],
            how = 'left',
            )
        data_with_info_grilles = data_with_info_grilles[
            ~data_with_info_grilles['date_effet_grille_{}'.format(annee)].isnull()
            ]
    return data_with_info_grilles


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
        data_ATT = data_annee.query("corps_NETNEH == '{}'".format(corps))
    else:
        data_ATT = data_annee
    data_ATT = data_ATT.rename(
        columns = {
            'c_cir': 'c_cir_{}'.format(annee),
            'ib': 'ib_{}'.format(annee),
            'annee_effet': 'annee_effet_{}'.format(annee),
            'date_effet_grille': 'date_effet_grille_{}'.format(annee)
            }
        )
    idents_keep = data_ATT.ident.unique().tolist()
    data_annee_1 = data.query('annee == {}'.format(annee - 1))
    data_annee_1 = data_annee_1[data_annee_1['ident'].isin(idents_keep)]
    data_annee_1 = data_annee_1.rename(
        columns = {
            "c_cir": "c_cir_{}".format(annee - 1),
            "ib": "ib_{}".format(annee - 1)
            }
        )
    data_annee_1 = data_annee_1[
        ['ident', 'c_cir_{}'.format(annee - 1), 'ib_{}'.format(annee - 1)]
        ]
    if annee == 2011:
        data_ATT = data_ATT[['ident',
                             'annee',
                             'c_cir_{}'.format(annee),
                             'ib_{}'.format(annee),
                             'annee_effet_{}'.format(annee),
                             'date_effet_grille_{}'.format(annee),
                             'corps_NETNEH'
                             ]]
    else:
        data_ATT = data_ATT[[
            'ident',
            'annee',
            'c_cir_{}'.format(annee),
            'ib_{}'.format(annee),
            'annee_effet_{}'.format(annee),
            'date_effet_grille_{}'.format(annee)
            ]]
    data_annee_annee_bef = data_ATT.merge(data_annee_1, on = 'ident', how = 'inner')
    return data_annee_annee_bef


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
    cas_uniques = data_annee_annee_bef[[
        "c_cir_{}".format(annee),
        "ib_{}".format(annee - 1),
        "date_effet_grille_{}".format(annee)
        ]].drop_duplicates(
            ["c_cir_{}".format(annee), "ib_{}".format(annee - 1)]
            )
    cas_uniques = cas_uniques.loc[:, ~cas_uniques.columns.duplicated()]
    return cas_uniques


def get_careers_chgmt_grade_annee_annee_bef(data_with_indicatrice_grade_change, chgmt_grade, annee):
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
    `annee` int
        année courante
    Returns
    ---------
    dataframe
        table des carrières des agents pour l'année et l'année précédente des agents qui changent ou ne changent pas de
        grade entre l'année et l'année précédente
    """
    data = data_with_indicatrice_grade_change
    if chgmt_grade:
        data = data.query('indicat_ch_grade_{} == True'.format(annee - 1))
        data['duree_initiale_dans_le_grade'] = 2011 - annee
    else:
        data = data.query('indicat_ch_grade_{} == False'.format(annee - 1))
    return data

