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
import os
import pandas as pd
from fonction_publique.base import (
    output_directory_path,
    grilles_path,
    table_corresp_grade_corps,
    grilles,
    project_path,
    )
from clean_data_initialisation import (
    merge_careers_with_grilles,
    clean_careers_annee_annee_bef,
    get_career_transitions_uniques_annee_annee_bef,
    clean_careers,
    get_careers_chgmt_grade_annee_annee_bef
    )
from impute_indicator_grade_change import (
    get_indicatrice_chgmt_grade_annee_annee_bef,
    map_transitions_uniques_annee_annee_bef_to_data,
    )

log = logging.getLogger(__name__)

# Paths
asset_path = os.path.join(output_directory_path, "select_data")

#def main(annee, annee_debut_observation, grilles, table_corresp_grade_corps, data_carrieres, generation_min,
#        corps, ib_manquant_a_exclure):
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
def main():
    data_carrieres = pd.read_csv(os.path.join(
        output_directory_path,
        "select_data",
        "corpsAT_1995.csv"
        )).query('annee > 2001')
    data_carrieres_clean = clean_careers(data_carrieres, 'ATT', True, 1960, grilles)
    data_carrieres_with_indicat_grade_chg = []  # Redefined at the end of the loop
    annees = list(reversed(range(2003, 2012)))
    data_a_utiliser_pour_annee_precedente = None
    for annee in annees:
        if annee == 2011:
            data_annee = merge_careers_with_grilles(data_carrieres_clean, grilles, annee)
        else:
            data_annee = merge_careers_with_grilles(data_a_utiliser_pour_annee_precedente, grilles, annee)
        #
        data_annee = clean_careers_annee_annee_bef(
            data_annee,
            data_carrieres,
            annee,
            'adjoints techniques territoriaux',
            )
        cas_uniques_annee_et_annee_bef = get_career_transitions_uniques_annee_annee_bef(data_annee, annee)
        cas_uniques_with_indic_grade_change = get_indicatrice_chgmt_grade_annee_annee_bef(
            cas_uniques_annee_et_annee_bef,
            True,
            annee,
            grilles,
            table_corresp_grade_corps
            )
        c_cir_bef_predits = (cas_uniques_with_indic_grade_change.query(
            '(indicat_ch_grade == True) & (ambiguite == False)').c_cir_bef_predit
            .value_counts(dropna = False)
            .index.tolist()
            )
        print c_cir_bef_predits
        assert 'TTH1' in c_cir_bef_predits

        assert len(cas_uniques_annee_et_annee_bef) <= len(cas_uniques_with_indic_grade_change)
        data_annee_with_indic_grade_change = map_transitions_uniques_annee_annee_bef_to_data(
            cas_uniques_with_indic_grade_change,
            data_annee,
            annee
            )
        c_cir_bef_predits = (data_annee_with_indic_grade_change
            .query('(indicat_ch_grade == True) & (ambiguite == False)')
            .c_cir_bef_predit
            .value_counts(dropna = False)
            .index.tolist()
            )
        assert 'TTH1' in c_cir_bef_predits, c_cir_bef_predits

        #
        if annee == 2003:  # dernière transition
            data_carrieres_with_indicat_grade_chg.append(data_annee_with_indic_grade_change)
        else:
            data_a_storer = get_careers_chgmt_grade_annee_annee_bef(
                data_annee_with_indic_grade_change,
                False,
                annee,
                )
            data_carrieres_with_indicat_grade_chg.append(data_a_storer)
            data_a_utiliser_pour_annee_precedente = get_careers_chgmt_grade_annee_annee_bef(
                data_annee_with_indic_grade_change,
                True,
                annee
                )

    data = pd.concat(data_carrieres_with_indicat_grade_chg).reset_index().drop_duplicates()
    assert len(data.reset_index().ident.unique()) == len(data_carrieres_clean.ident.unique())

    del data['corps_NETNEH_y']
    data_fin = data.sort_values(['ident', 'date_effet_grille'])
    data_fin = data.drop_duplicates(
        data_fin.columns.difference(['date_effet_grille', 'max_mois', 'min_mois']),
        keep = 'last'
        )
    assert len(data_fin.reset_index().ident.unique()) == len(data_carrieres_clean.ident.unique())

    data_fin.to_csv(os.path.join(
        output_directory_path,
        'imputation',
        'temp_data_2003_2011_5.csv'))


def main_continued():
    data_path = (os.path.join(
        output_directory_path,
        'imputation',
        'temp_data_2003_2011_5.csv'))

    data_career = pd.read_csv(data_path)
    del data_career['Unnamed: 0']

    data_career['annee'] = data_career['annee'] - 1
    del data_career['c_cir']
    data_career = data_career.rename(
        columns = {"c_cir_bef_predit" : "c_cir", "ib_bef" : "ib"}
        )
    data_career = data_career.sort_values(['ident', 'date_effet_grille'])
    data_career = data_career.drop_duplicates(data_career.columns.difference(
        ['date_effet_grille', 'max_mois', 'min_mois', 'echelon']), keep = "last"
        )

    data_career['temp_index'] = range(len(data_career))

    data_career_no_chgmt = data_career.query('(indicat_ch_grade == False) & (ambiguite == False)')[[
        'ident', 'annee'
        ]]
    data_career_no_chgmt = data_career_no_chgmt.groupby(['ident'], sort = False)['annee'].min().reset_index().rename(
        columns = {'annee': 'annee_min_non_chgmt_non_ambig'}
        )

    data_career_bis = data_career.merge(
        data_career_no_chgmt, on = ['ident']
        )
    data_career_annee_sup_grade_change = data_career_bis.query(
        '(annee > annee_min_non_chgmt_non_ambig) & (indicat_ch_grade)').temp_index.unique().tolist()
    ident_temp_index = data_career[
        data_career['temp_index'].isin(data_career_annee_sup_grade_change)
        ].reset_index().ident.tolist()
    data_career = data_career[~data_career['temp_index'].isin(data_career_annee_sup_grade_change)]
    del data_career['temp_index']
    data_career = data_career.reset_index()

    data_career = data_career.merge(data_career_no_chgmt, on = 'ident', how = 'outer')
    data_career['annee_min_non_chgmt_non_ambig'] = data_career['annee_min_non_chgmt_non_ambig'].fillna(55555)

    data_career.loc[
        ((data_career['ident'].isin(ident_temp_index))) & (
            data_career['annee'] > data_career['annee_min_non_chgmt_non_ambig']
            ), ['ambiguite']] = False

    data_career.to_csv(
        os.path.join(
            output_directory_path,
            "imputation",
            "data_2003_2011_5.csv"
            )
        )


if  __name__ == '__main__':
    main()
