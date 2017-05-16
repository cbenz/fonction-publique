# -*- coding: utf-8 -*-

from __future__ import division

import logging
import numpy as np
import os
import pandas as pd


log = logging.getLogger(__name__)


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

data_2011 = data.query('annee == 2011')
log.info("Il y a {} agents qui sont ATT en 2011 selon leur c_cir".format(
    len(data_2011[data_2011['c_cir'].isin(['TTH1', 'TTH2', 'TTH3', 'TTH4'])].ident.unique())
    ))


def clean_grille(grilles, short):
    grilles['date_effet_grille'] = pd.to_datetime(grilles.date_effet_grille)
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
    grilles['date_effet_grille'] = pd.to_datetime(grilles.date_effet_grille)

    dict_corres_NETNEH = corresp_corps.set_index('CodeNETNEH')['cadredemploiNETNEH'].to_dict()
    grilles['corps_NETNEH'] = grilles['code_grade_NETNEH'].map(dict_corres_NETNEH)

    if short:
        grilles = grilles[
            ['c_cir', 'date_effet_grille']
            ].drop_duplicates()
    else:
        grilles = grilles
    return grilles


def clean_data_carriere_initial(data, corps, ib_manquant_a_exclure, generation_min):
    "retourne un df des carrières entre 2007 et 2011 des agents qui sont replaçables dans le corps des AT en"
    "2011, qui n'ont pas d'IB valant -1 sur la période 2007-2015, qui ont un c_cir suivant leur c_cir de 2011"
    "renseigné s'il existe et qui sont d'une génération postérieure à la génération minimale.    "

    tracking = []
    tracking.append(['Aucun', len(data.ident.unique())])

    if corps == "ATT":
        ident_keep_in_corps_2011 = data[(
            data['annee'] == 2011) & (data['c_cir'].isin(['TTH1', 'TTH2', 'TTH3', 'TTH4']))
            ].ident.unique()
        data = data[data['ident'].isin(ident_keep_in_corps_2011)]
        tracking.append(['Corps des {} en 2011'.format('ATT'), len(data.ident.unique())])

    data = data[['ident', 'annee', 'c_cir', 'ib4', 'echelon4', 'generation', 'etat4']].rename(
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
        tracking.append([r'IB manquant entre 2007 et 2015', len(data.ident.unique())])

    # On veut les identifiants qui sont rattachables à une grille en 2011
    idents_to_keep_on_grilles_in_2011 = merge_careers_w_grille(data, grilles, 2011).ident.unique()
    data = data[data['ident'].isin(idents_to_keep_on_grilles_in_2011)]
    tracking.append([r'Rattaché à une grille en 2011', len(data.ident.unique())])

    tracking = pd.DataFrame(tracking)
    print(tracking.to_latex())
    return data


def merge_careers_w_grille(data, grilles, annee):
    "retourne un df des carrières à t des agents qu'on a pu positionner sur"
    "une grille à t"

    if annee == 2011:
        data = data.query('annee == {}'.format(annee)).rename(columns = {"ib4": "ib"})
#        condition_1 = (
#            (data['c_cir'].isnull()
#            ) | data['echelon4'].isnull())
#        data = data[~(condition_1)]
#        print "En supprimant les individus dont le c_cir ou l'échelon est nul en {}, on a {} agents".format(
#           annee, len(data.ident.unique()))
#
#        data = data[~data['echelon4'].isnull()]
#        data['echelon'] = data['echelon4'].astype(int)
#        data['echelon'] = data['echelon'].astype(str)
#        data['echelon'] = data['echelon'].str.zfill(2)
    else:
        data = data
        data["annee"] = annee

#    grilles['date_effet_grille'] = pd.to_datetime(grilles.date_effet_grille)
#    grilles.sort_values('date_effet_grille', inplace = True)
#
#    grilles['c_cir'] = grilles['code_grade_NETNEH'].astype(str)
#    grilles['echelon']= grilles['echelon'].astype(str)
#    grilles['annee_effet'] = (
#        pd.to_datetime(np.array(
#                        grilles.date_effet_grille.astype(str),
#                        dtype='datetime64[Y]'))).year
#    grilles['date_effet_grille'] = (
#        pd.to_datetime(grilles.date_effet_grille)
#        )
#
#    dict_corres_NETNEH = corresp_corps.set_index(
#        'CodeNETNEH'
#        )['cadredemploiNETNEH'].to_dict()
#    grilles['corps_NETNEH'] = grilles[
#            'code_grade_NETNEH'
#            ].map(dict_corres_NETNEH)
#
#    grilles_short = grilles[[
#            'c_cir',
#            'date_effet_grille'
#            ]].drop_duplicates()

    grilles = clean_grille(grilles, short = False)
    grilles_short = clean_grille(grilles, short = True)

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

    #
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

        data_with_date_effet_grille = data.merge(df_corres,
                  on = ['c_cir', 'annee'], how = 'left')

        data_with_info_grilles = data_with_date_effet_grille.merge(
            grilles, on = ['date_effet_grille', 'c_cir', 'ib'], how = 'left'
            )

        data_with_info_grilles = data_with_info_grilles[
            ~data_with_info_grilles['date_effet_grille'].isnull()
            ]

    else:
        df_corres = pd.DataFrame(
            list_c_cir_dates_obs_effet,
            columns = ['c_cir_{}_predit'.format(annee), 'annee', 'date_effet_grille_{}'.format(annee)],
            )

        data_with_date_effet_grille = data.merge(
            df_corres,
            on = ['c_cir_{}_predit'.format(annee), 'annee', 'date_effet_grille_{}'.format(annee)],
            how = 'left',
            )

        grilles['c_cir_{}_predit'.format(annee)] = grilles['c_cir']  # FIXME
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

    data_with_info_grilles = data_with_info_grilles[
        ~data_with_info_grilles['code_grade_NETNEH'].isnull()
        ]

#    print "En ne gardant que les individus qu'on peut rattacher à une grille en {}, on a {} agents".format(
#            annee, len(data_with_info_grilles)
#            )
    return data_with_info_grilles


def clean_careers_t_t_1(data_t, data, annee, corps):
    "on travaille uniquement sur les agents appartenant aux ATT pour"
    "annee = annee et dont l'ib est informatif à t-1, retourne un df"
    "mergé des années t et t-1"
    # print data_t.head()
    if annee == 2011:
        data_ATT = data_t.query("corps_NETNEH == '{}'".format(corps))

    else:
        data_ATT = data_t

    data_ATT = data_ATT.rename(
        columns = {
            'c_cir': 'c_cir_{}'.format(annee),
            'ib': 'ib_{}'.format(annee),
            'annee_effet': 'annee_effet_{}'.format(annee),
            'date_effet_grille': 'date_effet_grille_{}'.format(annee)
            }
        )

    idents_keep = data_ATT.ident.unique().tolist()
    # print idents_keep
    data_t_1 = data.query('annee == {}'.format(annee - 1))
    data_t_1 = data_t_1[data_t_1['ident'].isin(idents_keep)]
    # print data_t_1.head()
    # print data_ATT.head()
    # data_t_1 = data_t_1[~data_t_1['ib4'].isin([0, 'NaN', -1])]

    data_t_1 = data_t_1.rename(
        columns = {
            "c_cir": "c_cir_{}".format(annee - 1),
            "ib": "ib_{}".format(annee - 1)
            }
        )
    data_t_1 = data_t_1[
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
    data = data_ATT.merge(data_t_1, on = 'ident', how = 'inner')
    print("Après fusion des infos pour l'année {} et {}, on garde {} agents".format(annee, annee - 1,
        len(data.ident.unique())
        ))
    return data


def get_cas_uniques(data, annee):
    "cas uniques définis comme uniques correspondances entre code cir à t,"
    "ib à t-1"

    cas_uniques = data[[
        "c_cir_{}".format(annee),
        "ib_{}".format(annee - 1),
        "date_effet_grille_{}".format(annee)
        ]].drop_duplicates(
            ["c_cir_{}".format(annee), "ib_{}".format(annee - 1)]
            )
    cas_uniques = cas_uniques.loc[:, ~cas_uniques.columns.duplicated()]
    return cas_uniques


# data_2012 = merge_careers_w_grille(data, grilles, corresp_corps, 2012)
# data_2012 = clean_careers_t_t_1(data_2012,
#                                 data,
#                                 2012,
#                                 'adjoints techniques territoriaux'
#                                 )
# cas_uniques_2012_2013 = get_cas_uniques(data_2012, 2012)
