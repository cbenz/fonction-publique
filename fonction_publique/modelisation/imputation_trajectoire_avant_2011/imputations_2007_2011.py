# -*- coding: utf-8 -*-
"""
Date dernier edit: 23/05/2017
Auteur : Lisa Degalle

Objectif : imputation_2007_2011.py a pour but d'attribuer à chaque agent pour chaque année entre 2007 et 2011 une
indicatrice de changement de grade et un statut d'ambiguité pour cette indicatrice de changement de grade. Ce fichier
utilise toutes les fonctions définies dans clean_data_initialisation et
imputation_indicatrice_chgmt_grade_annee_annee_bef

Inputs :
    - inputs requis par clean_data_initialisation
    - fonctions définies dans clean_data_initialisation et imputation_indicatrice_chgmt_grade_annee_annee_bef.py

Outputs (utilisés comme inputs dans imputations_2007_2011.py):
    - cas uniques de transitions de carrières avec une indicatrice de changement de grade et un degré de certitude
    (TOFIX: appelé statut d'ambiguité)
    - données de carrières avec une indicatrice de chgmt de grade et un statut d'ambiguité pour année courante et année
    précédente

Fonctions :
    - main
"""

from __future__ import division
import logging
import numpy as np
import os
import pandas as pd
import pkg_resources
import sys
from fonction_publique.base import output_directory_path
from clean_data_initialisation import (
    merge_careers_with_grilles,
    clean_careers_annee_annee_bef,
    get_career_transitions_uniques_annee_annee_bef,
    clean_careers,
    get_careers_chgmt_grade_annee_annee_bef
    )
from imputation_indicatrice_chgmt_grade_annee_annee_bef import (
    get_indicatrice_chgmt_grade_annee_annee_bef,
    map_transitions_uniques_annee_annee_bef_to_data,
    )

log = logging.getLogger(__name__)

# Paths
asset_path = os.path.join(output_directory_path, r"bases_AT_imputations_trajectoires_2006_2011")
CNRACL_project_path = os.path.join(
    pkg_resources.get_distribution('fonction_publique').location,
    'fonction_publique'
    )
grilles_path = os.path.join(CNRACL_project_path, "assets")

def main(annee,
         annee_debut_observation,
         grilles,
         table_corresp_grade_corps,
         data_carrieres,
         generation_min,
         corps,
         ib_manquant_a_exclure,
         results_path,
         filename_data_chgmt,
         filename_data_non_chgmt,
         ):

    """
    On boucle sur les années à partir de l'annee_debut_observation jusqu'à année = annee, inversée
    1. On obtient d'abord les données de carrières complètes nettoyées, puis
    2. les données de l'année en cours contenant les informations de grilles de
    chaque agent cette année-là, puis
    3. on ajoute une variable pour l'ib de l'agent l'année précédente, puis
    4. on extrait les cas uniques de transitions d'état de carrière entre l'année moins un et l'année en cours, puis
    5. on assigne une indicatrice de changement de grade et un statut d'ambiguité à ces cas uniques, puis
    6. on attribue à chaque agent une indicatrice de changement de grade et un statut d'ambiguité en suivant les
    résultats donnés sur les cas uniques, puis
    7. on divise les transitions individuelles en deux groupes: les transitions avec et les transitions sans
    changement de grade. On stocke les transitions avec changement de grade dans une liste.
    On recommence la procédure initiale pour l'année précédent l'année courante moins un avec les transitions sans
    changement de grade entre l'année précédente et l'année en cours.
    ...on répète la procédure jusqu'à l'annee_debut_observation...
    8. on stocke dans deux fichiers csv les carrières des agents ayant changé de grade sur la période et les agents
    n'ayant pas changé de grade sur la période. (Une ligne = un individu)

    Note : un agent-année peut donc être présent dans les deux fichier csv s'il est dans un statut ambigu pour cette
    année

    Parameters:
    ----------
    `annee`: int
        année de début d'observation complète (i.e chaque ident année après cette année est a prior rattachable à une
        grille)
    `annee_debut_observation`: int
        année de début d'observation pour l'imputation de la durée déjà passée dans le grade à annee = annee
    `grilles`: dataframe
    `table_corresp_grade_corps`: dataframe
    `data_carrieres`: dataframe
    `generation_min`: int
    `corps`: str
    `ib_manquant_a_exclure`: bool
    `results_path`: str
        dossier où seront storés les deux fichiers de résultats
    `filename_data_chgmt`: str
        nom du fichier csv de résultats pour les individus ayant changé de grade entre 2007 et 2011
    `filename_data_non_chgmt`: str
        nom du fichier csv de résultats pour les individus n'ayant pas changé de grade entre 2007 et 2011

    Returns:
    ----------
    2 csv files
         dataframe de résultats pour les individus ayant changé de grade entre 2007 et 2011
         dataframe de résultats pour les individus n'ayant pas changé de grade entre 2007 et 2011
    """
    data_carrieres = clean_careers(data_carrieres, 'ATT', True, 1960, grilles)
    liste_data_individus_ayant_change_de_grade = []
    liste_data_individs_nayant_pas_change_de_grade_en_2007 = []
    data_a_utiliser_pour_annee_precedente = None  # Redefined at the end of the loop
    annees = list(reversed(range(annee_debut_observation, 2012)))
    for annee in annees:
        if annee == 2011:
            data = data_carrieres
        else:
            data = data_a_utiliser_pour_annee_precedente
        data_annee = merge_careers_with_grilles(data, grilles, annee)

        data_annee = clean_careers_annee_annee_bef(
            data_annee,
            data_carrieres,
            annee,
            'adjoints techniques territoriaux',
            )
        cas_uniques_annee_et_annee_bef = get_career_transitions_uniques_annee_annee_bef(data_annee, annee)
        cas_uniques_annee_et_annee_bef_avec_grades_predits = get_indicatrice_chgmt_grade_annee_annee_bef(
            cas_uniques_annee_et_annee_bef,
            True,
            annee,
            grilles,
            table_corresp_grade_corps,
            )
        data_annee_et_annee_bef_avec_grades_predits = map_transitions_uniques_annee_annee_bef_to_data(
            cas_uniques_annee_et_annee_bef_avec_grades_predits,
            data_annee,
            annee,
            )
        data_a_utiliser_pour_annee_precedente = get_careers_chgmt_grade_annee_annee_bef(
            data_annee_et_annee_bef_avec_grades_predits,
            False,
            annee,
            )
        log.info("Il y a {} agents qui ne changent peut-être pas ou certainement pas de grade en {}".format(
            len(data_a_utiliser_pour_annee_precedente), annee)
            )
        data_a_storer = get_careers_chgmt_grade_annee_annee_bef(
            data_annee_et_annee_bef_avec_grades_predits,
            True,
            annee,
            )
        log.info("Il y a {} agents qui changent peut-être ou certainement de grade en {}".format(
            len(data_a_storer), annee))
        liste_data_individus_ayant_change_de_grade.append(data_a_storer)
        if annee == 2007:
            data_a_storer_indiv_ne_changeant_pas_de_grade_apres_2007 = get_careers_chgmt_grade_annee_annee_bef(
                data_annee_et_annee_bef_avec_grades_predits,
                False,
                annee,
                )
            liste_data_individs_nayant_pas_change_de_grade_en_2007.append(
                data_a_storer_indiv_ne_changeant_pas_de_grade_apres_2007
                )
    liste_df = []
    for df in liste_data_individus_ayant_change_de_grade:
        if len(df) != len(df.ident.unique()):
            df = df.drop_duplicates('ident', keep="last")
        else:
            df = df
        liste_df.append(df)
    dfs = [df.set_index('ident') for df in liste_df]
    resultat_chgmt_de_grade = pd.concat(dfs, axis=1).reset_index()
    resultat_chgmt_de_grade.to_csv(os.path.join(results_path, filename_data_chgmt))
    resultat_non_chgmt_de_grade = pd.concat(liste_data_individs_nayant_pas_change_de_grade_en_2007)
    resultat_non_chgmt_de_grade.to_csv(os.path.join(results_path, filename_data_non_chgmt))
    return


if __name__ == '__main__':
#    logging.basicconfig(level = logging.info, stream = sys.stdout) # AttributeError: 'module' object has no attribute 'basicconfig'
    main(
        annee = 2011,
        annee_debut_observation = 2007,
        grilles = pd.read_hdf(
            os.path.join(grilles_path, 'grilles_fonction_publique/grilles_old.h5')
            ),
        table_corresp_grade_corps = pd.read_csv(
            os.path.join(grilles_path, 'corresp_neg_netneh.csv'),
            delimiter = ';'
            ),
        data_carrieres = pd.read_csv(os.path.join(asset_path, "corpsAT_2006.csv")), # pd.read_csv(
#   os.path.join(output_directory_path, "bases_AT_imputations_trajectoires_1995_2011/corpsAT_1995.csv")
#    )
        generation_min = 1960,
        corps = 'ATT',
        ib_manquant_a_exclure = True,
        results_path = os.path.join(output_directory_path, "base_AT_clean_2006_2011"),
        filename_data_chgmt = "data_changement_grade_2006_2011_t.csv",
        filename_data_non_chgmt = "data_non_changement_grade_2006_2011_t.csv",
        )