# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 18:32:28 2017

@author: l.degalle
"""

from __future__ import division

import numpy as np
import os
import pandas as pd


from clean_data_initialisation import merge_careers_w_grille, clean_careers_t_t_1, get_cas_uniques


# Paths
asset_path = r"M:\CNRACL\output\bases_AT_imputations_trajectoires_avant_2011"
grilles_path = 'C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/assets/'

# Data
data = pd.read_csv(os.path.join(asset_path, "corpsAT_2007.csv"))
grilles = pd.read_hdf(
    os.path.join(grilles_path, 'grilles_fonction_publique/grilles_old.h5')
    )
corresp_corps = pd.read_csv(
    os.path.join(grilles_path, 'corresp_neg_netneh.csv'),
    delimiter = ';'
    )

# data_2012 = merge_careers_w_grille(data, grilles, corresp_corps, 2012)
# data_2012 = clean_careers_t_t_1(data_2012, data, 2012)
# cas_uniques_2012_2013 = get_cas_uniques(data_2012, 2012)


def impute_indicatrice_chgmt_grade(data_cas_uniques, transit_intra_corps, annee):
    """impute indicatrice de changement de grade aux cas uniques,"""
    """si transit_intra_corps = True, on ne considère comme possibles que les"""
    """transitions de grade à l'intérieur d'un même grade"""

    cas_uniques = data_cas_uniques

    cas_uniques_with_indic_chgmt_grade = []

    for cas in range(len(cas_uniques)):

        cas_unique = cas_uniques.iloc[cas]

        c_cir_now = str(cas_unique['c_cir_{}'.format(annee)])

        date_effet_grille_now = pd.to_datetime(cas_unique['date_effet_grille_{}'.format(annee)])

        ib_bef = int(cas_unique['ib_{}'.format(annee - 1)])
        dict_corres_NETNEH = corresp_corps.set_index('CodeNETNEH')['cadredemploiNETNEH'].to_dict()
        grilles['corps_NETNEH'] = grilles['code_grade_NETNEH'].map(dict_corres_NETNEH)

        date_effet_grille_bef = grilles[
            (grilles['code_grade_NETNEH'] == c_cir_now) &
            (grilles['date_effet_grille'] <= pd.datetime(annee - 1, 12, 31))
            ].date_effet_grille.max()

        if annee == 2009:
            # on a remarque que beaucoup d'agents ne sont certainement pas
            # places sur leur grille de 2008 directement après la réforme fin 2008,
            # on regarde donc si leur IB de 2008 est présent sur une des grilles prenant effet
            # à la dernière réforme avant la réforme de 2008 ou sur la grille
            # prenant effet en 2008
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
            # Il y a changement de grade à t
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
                    ]).transpose().rename(columns = {
                        0: "c_cir_{}".format(annee),
                        1: "ib_{}".format(annee - 1),
                        2: "date_effet_grille_{}".format(annee),
                        3: "c_cir_{}_predit".format(annee - 1),
                        4: "rang_grade_possible_{}".format(annee - 1),
                        5: "nombre_de_grades_possibles_{}".format(annee - 1),
                        6: "ambiguite_{}".format(annee - 1),
                        7: "indicat_ch_grade_{}".format(annee - 1)
                        })
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
                    ]).transpose().rename(columns = {
                        0: "c_cir_{}".format(annee),
                        1: "ib_{}".format(annee - 1),
                        2: "date_effet_grille_{}".format(annee),
                        3: "c_cir_{}_predit".format(annee - 1),
                        4: "rang_grade_possible_{}".format(annee - 1),
                        5: "nombre_de_grades_possibles_{}".format(annee - 1),
                        6: "ambiguite_{}".format(annee - 1),
                        7: "indicat_ch_grade_{}".format(annee - 1)
                        })
                )

        else:
            # Il y a incertitude
            if transit_intra_corps:
                # On ne s'intéresse qu'aux transitions à l'intérieur du corps
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
#                if annee == 2009:
#                    print grilles_possibles.date_effet_grille.unique()
#                    print grades_possibles_bef.head()

                grades_possibles_bef["c_cir_{}".format(annee)] = [c_cir_now] * len(grades_possibles_bef)
                grades_possibles_bef["ib_{}".format(annee - 1)] = [ib_bef] * len(grades_possibles_bef)
                grades_possibles_bef[
                    "date_effet_grille_{}".format(annee)
                    ] = [date_effet_grille_now] * len(grades_possibles_bef)

                grades_possibles_bef[
                    "indicat_ch_grade_{}".format(annee - 1)
                    ] = (
                        grades_possibles_bef["c_cir_{}".format(annee)] !=
                        grades_possibles_bef["c_cir_{}_predit".format(annee - 1)]
                        )

                c_neg_now = int(
                    grades_possibles_bef.query(
                        'indicat_ch_grade_{} == False'.format(annee - 1)
                        )['c_neg_{}_predit'.format(annee - 1)].unique())

                grades_possibles_bef = grades_possibles_bef.query(
                    'c_neg_{}_predit <= {}'.format(annee - 1, c_neg_now))

                grades_possibles_bef = grades_possibles_bef.query(
                    'c_neg_{}_predit > {}'.format(annee - 1, c_neg_now - 2)
                    )

                grades_possibles_bef[
                    'nombre_de_grades_possibles_{}'.format((annee - 1))
                    ] = len(grades_possibles_bef)

                grades_possibles_bef[
                    'rang_grade_possible_{}'.format(annee - 1)
                    ] = range(1, len(grades_possibles_bef) + 1)

                grades_possibles_bef[
                    "ambiguite_{}".format(annee - 1)
                    ] = (
                    len(grades_possibles_bef['indicat_ch_grade_{}'.format(annee - 1)].value_counts()) != 1
                    )

                grades_possibles_bef = grades_possibles_bef.drop_duplicates(
                    grades_possibles_bef.columns.difference(['date_effet_grille_{}'.format(annee - 1)])
                    )
                # print grades_possibles_bef
                cas_uniques_with_indic_chgmt_grade.append(grades_possibles_bef)

            else:
                stop
                # FIXME

    cas_uniques_w_indic_df = pd.concat(cas_uniques_with_indic_chgmt_grade)

    return cas_uniques_w_indic_df


# cas_uniques_with_indicatrice_chgmt_grade = impute_indicatrice_chgmt_grade(cas_uniques_2012_2013, True, 2012)


def map_cas_uniques_to_data(cas_uniques_w_indic_df, data, annee, test):
    cas_uniques = cas_uniques_w_indic_df
    data = data

    data_with_indicatrice_grade_change = data.merge(
        cas_uniques,
        how = 'outer',
        on = ['c_cir_{}'.format(annee),
        'ib_{}'.format(annee - 1)]
        )
    if test:
        data_with_indicatrice_grade_change = data_with_indicatrice_grade_change[[
            'ident',
            'c_cir_{}'.format(annee),
            'ib_{}'.format(annee),
            'date_effet_grille_{}_x'.format(annee),
            'ib_{}'.format(annee - 1),
            'ambiguite_{}'.format(annee - 1),
            'c_cir_{}_predit'.format(annee - 1),
            'c_cir_{}'.format(annee - 1),
            'indicat_ch_grade_{}'.format(annee - 1),
            'nombre_de_grades_possibles_{}'.format(annee - 1),
            'rang_grade_possible_{}'.format(annee - 1)
            ]]
    else:
        data_with_indicatrice_grade_change = data_with_indicatrice_grade_change[[
            'ident',
            'c_cir_{}'.format(annee),
            'ib_{}'.format(annee),
            'date_effet_grille_{}_x'.format(annee),
            'date_effet_grille_{}'.format(annee -1),
            'ib_{}'.format(annee - 1),
            'ambiguite_{}'.format(annee - 1),
            'c_cir_{}_predit'.format(annee - 1),
            'indicat_ch_grade_{}'.format(annee - 1),
            'nombre_de_grades_possibles_{}'.format(annee - 1),
            'rang_grade_possible_{}'.format(annee - 1)
            ]]
    data_with_indicatrice_grade_change = data_with_indicatrice_grade_change.rename(
        columns = {
            "date_effet_grille_{}_x".format(annee): "date_effet_grille_{}".format(annee)
            }
        )
    return data_with_indicatrice_grade_change


# data_2012_with_possible_grades_2011 = map_cas_uniques_to_data(
#         cas_uniques_with_indicatrice_chgmt_grade,
#         data_2012,
#         2012
#         )


def get_indiv_who_change_grade_or_not_at_t(data_with_indicatrice_grade_change, change, annee):
    data = data_with_indicatrice_grade_change
    if change:
        data = data.query('indicat_ch_grade_{} == True'.format(annee - 1))
        data['duree_initiale_dans_le_grade'] = 2011 - annee
    else:
        data = data.query('indicat_ch_grade_{} == False'.format(annee - 1))
    return data


# TEST sur cas classés "non ambigus"
def test_sur_2011():
    data_2012 = merge_careers_w_grille(data, grilles, corresp_corps, 2012)
    data_2012 = clean_careers_t_t_1(data_2012, data, 2012)
    cas_uniques_2012_2013 = get_cas_uniques(data_2012, 2012)
    cas_uniques_with_indicatrice_chgmt_grade = impute_indicatrice_chgmt_grade(
        cas_uniques_2012_2013,
        True,
        2012
        )
    data_2012_2011 = map_cas_uniques_to_data(
        cas_uniques_with_indicatrice_chgmt_grade,
        data_2012,
        2012,
        test = True
        )
    return data_2012_2011
    #    data_test = data_2012_2011.query(
    #        "(ambiguite_2011 == False)"
    #        )
    #
    #    test_faux_positif = data_test[
    #            (data_test['c_cir_2012'] == data_test['c_cir_2011']) & data_test['indicat_ch_grade_2011'] == True
    #            ]
    #    tx_1 = r"Sur les {} cas non ambigus pour lesquels on predit un changement de grade entre 2011 et 2012, on se trompe sur {}, soit {} de taux d'erreur".format(len(data_test),len(test_faux_positif), len(test_faux_positif)/len(data_test))
    #
    #    test_faux_negatif = data_test[
    #            (data_test['c_cir_2012'] != data_test['c_cir_2011']) & (data_test['indicat_ch_grade_2011'] == False)
    #            ]
    #    tx_2 = r"Sur les {} cas non ambigus pour lesquels on ne predit pas un changement de grade entre 2011 et 2012, on se trompe sur {}, soit {} de taux d'erreur".format(len(data_test), len(test_faux_negatif), len(test_faux_negatif)/len(data_test))
    #
    #    return tx_1, tx_2