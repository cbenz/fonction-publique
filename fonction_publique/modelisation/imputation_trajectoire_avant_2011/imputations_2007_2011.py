# -*- coding: utf-8 -*-


from __future__ import division

import logging
import numpy as np
import os
import pandas as pd
import pkg_resources
import sys

from fonction_publique.base import output_directory_path

from clean_data_initialisation import (
    merge_careers_w_grille,
    clean_careers_t_t_1,
    get_cas_uniques,
    clean_data_carriere_initial
    )
from imputation_indicatrice_de_changement_de_grade_retrospective import (
    impute_indicatrice_chgmt_grade,
    map_cas_uniques_to_data,
    get_indiv_who_change_grade_or_not_at_t
    )


log = logging.getLogger(__name__)


# Paths
asset_path = os.path.join(output_directory_path, r"bases_AT_imputations_trajectoires_avant_2011")

CNRACL_project_path = os.path.join(
    pkg_resources.get_distribution('fonction_publique').location,
    'fonction_publique'
    )
grilles_path = os.path.join(CNRACL_project_path, "assets")
results_filename = os.path.join(
    CNRACL_project_path, "modelisation/imputation_trajectoire_avant_2011/resultats_imputation_2006_2011.csv"
    )

# Data
data_carrieres_2007 = pd.read_csv(os.path.join(asset_path, "corpsAT_2007.csv"))
#data_carrieres_1995_2015 = pd.read_csv(
#    "M:/CNRACL/output/bases_AT_imputations_trajectoires_1995_2011/corpsAT_1995.csv"
#    )
grilles = pd.read_hdf(
    os.path.join(grilles_path, 'grilles_fonction_publique/grilles_old.h5')
    )
corresp_corps = pd.read_csv(
    os.path.join(grilles_path, 'corresp_neg_netneh.csv'),
    delimiter = ';'
    )

annees = list(reversed(range(2008, 2012)))


def main(annee,
         grilles,
         corresp_corps,
         data_carrieres_2007,
         generation_min,
         corps,
         ib_manquant_a_exclure,
         results_path,
         filename_data_chgmt,
         filename_data_non_chgmt,
         ):

    data_carrieres_2007 = clean_data_carriere_initial(
        data_carrieres_2007,
        'ATT',
        True,
        1960
        )

    liste_data_individus_ayant_change_de_grade = []
    liste_data_individs_nayant_pas_change_de_grade_en_2007 = []

    data_a_utiliser_pour_annee_precedente = None  # Redefined at the end of the loop
    for annee in annees:
        if annee == 2011:
            data = data_carrieres_2007
        else:
            data = data_a_utiliser_pour_annee_precedente

        if annee == 2007:
            print data.head()
        data_annee = merge_careers_w_grille(data, grilles, annee)
        if annee == 2007:
            print data_annee.head()
        data_annee = clean_careers_t_t_1(data_annee, data_carrieres_2007, annee, 'adjoints techniques territoriaux')
        cas_uniques_annee_et_annee_bef = get_cas_uniques(data_annee, annee)

        cas_uniques_annee_et_annee_bef_avec_grades_predits = impute_indicatrice_chgmt_grade(
            cas_uniques_annee_et_annee_bef,
            True,
            annee
            )

        data_annee_et_annee_bef_avec_grades_predits = map_cas_uniques_to_data(
            cas_uniques_annee_et_annee_bef_avec_grades_predits,
            data_annee,
            annee,
            False
            )

        data_a_utiliser_pour_annee_precedente = get_indiv_who_change_grade_or_not_at_t(
            data_annee_et_annee_bef_avec_grades_predits,
            False,
            annee,
            )
        print data_a_utiliser_pour_annee_precedente.head()
        log.info("Il y a {} agents qui ne changent peut-être pas ou certainement pas de grade en {}".format(
            len(data_a_utiliser_pour_annee_precedente), annee)
            )
        data_a_storer = get_indiv_who_change_grade_or_not_at_t(
            data_annee_et_annee_bef_avec_grades_predits,
            True,
            annee,
            )
        log.info("Il y a {} agents qui changent peut-être ou certainement de grade en {}".format(
            len(data_a_storer), annee))

        liste_data_individus_ayant_change_de_grade.append(data_a_storer)

        if annee == 2008:
            data_a_storer_indiv_ne_changeant_pas_de_grade_apres_2007 = get_indiv_who_change_grade_or_not_at_t(
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
    resultat_chgmt_de_grade_certain = resultat_chgmt_de_grade[
        resultat_chgmt_de_grade['ambiguite_2007'].isin([False, np.nan])
        ]

    resultat_chgmt_de_grade.to_csv(os.path.join(results_path, filename_data_chgmt))

    resultat_non_chgmt_de_grade = pd.concat(liste_data_individs_nayant_pas_change_de_grade_en_2007)

    resultat_non_chgmt_de_grade.to_csv(os.path.join(results_path, filename_data_non_chgmt))

    return resultat_chgmt_de_grade_certain


if __name__ == '__main__':
#    logging.basicconfig(level = logging.info, stream = sys.stdout)
    main(
        2011,
        grilles,
        corresp_corps,
        data_carrieres_2007,
        1960,
        'ATT',
        True,
        results_path = "", #"M:/CNRACL/output/base_AT_clean_2007_2011",
        filename_data_chgmt ="", #"data_changement_grade_2007_2011.csv",
        filename_data_non_chgmt = "", #"data_non_changement_grade_2007_2011.csv",
        )


result_non_chg = pd.read_csv("M:/CNRACL/output/base_AT_clean_2007_2011/data_non_changement_grade_2007_2011.csv")
result_chg = pd.read_csv("M:/CNRACL/output/base_AT_clean_2007_2011/data_changement_grade_2007_2011.csv")
len(set(result_chg.ident.unique().tolist() + result_non_chg.ident.unique().tolist()))

# resultat_non_chgmt_de_grade = pd.concat(
#        liste_data_individs_nayant_pas_change_de_grade_en_2007
#        )
#
# resultat_non_chgmt_de_grade.to_csv('')

# ident_chgmt = resultat_chgmt_de_grade.reset_index().ident.unique().tolist()
# ident_non_chgmt = resultat_non_chgmt_de_grade.reset_index().ident.unique().tolist()
# liste = ident_chgmt + ident_non_chgmt
#
#
#
# resultat_chgmt_de_grade.query('ambiguite_2007 == True')
#
# resultat_non_chgmt_de_grade.query('ambiguite_2007 == True').ident.unique()

# ib_informatifs_selectionnes = True
# enlarge_set_possible_grilles_2009 = True
# if annees == list(reversed(range(2008, 2012))):
#     if ib_informatifs_selectionnes == False:
#        resultat_chgmt_de_grade.to_csv(
#                "C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/modelisation/imputation_trajectoire_avant_2011/resultats_imputation_2007-2011_chgmt.csv"
#                )
#
#        resultat_non_chgmt_de_grade.to_csv(
#                "C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/modelisation/imputation_trajectoire_avant_2011/resultats_imputation_2007-2011_non_chgmt.csv"
#                )
#     else:
#         if enlarge_set_possible_grilles_2009 == True:
#             resultat_chgmt_de_grade.to_csv(
#                     "C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/modelisation/imputation_trajectoire_avant_2011/resultats_imputation_2007-2011_chgmt_sans_selection_sur_ib_informatif_enlarge_grille_possibles_2009.csv"
#                     )
#             resultat_non_chgmt_de_grade.to_csv(
#                    "C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/modelisation/imputation_trajectoire_avant_2011/resultats_imputation_2007-2011_non_chgmt_sans_selection_sur_ib_informatif_enlarge_grille_possibles_2009.csv"
#                    )
#         else:
#             resultat_chgmt_de_grade.to_csv(
#                    "C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/modelisation/imputation_trajectoire_avant_2011/resultats_imputation_2007-2011_chgmt_sans_selection_sur_ib_informatif.csv"
#                    )
#
#             resultat_non_chgmt_de_grade.to_csv(
#                    "C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/modelisation/imputation_trajectoire_avant_2011/resultats_imputation_2007-2011_non_chgmt_sans_selection_sur_ib_informatif.csv"
#                    )
#
# if liste_annees == list(reversed(range(2007, 2012))) & (ib_informatifs_selectionnes == False):
#    resultat_chgmt_de_grade.to_csv(
#            "C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/modelisation/imputation_trajectoire_avant_2011/resultats_imputation_2006-2011.csv"
#            )
