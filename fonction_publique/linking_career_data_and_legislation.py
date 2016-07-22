# -*- coding:utf-8 -*-


from __future__ import division
import numpy as np
import os
import pandas as pd
import pylab as plt
import seaborn as sns
from datetime import datetime, timedelta, date
import dateutil.parser as parser
from collections import Counter

from fonction_publique.base import asset_path, hdf_directory_path, hdf5_file_path

DEBUG = True

debug_chunk_size = 100000 if DEBUG else None
carrieres_a_lier_file_path = os.path.join(
    hdf_directory_path,
    "carrieres_a_lier_debug.hdf5",
    ) if DEBUG else os.path.join(
        hdf_directory_path,
        "carrieres_a_lier",
        )
etats_uniques_file_path = os.path.join(
    hdf_directory_path,
    "etats_uniques_debug.hdf5",
    ) if DEBUG else os.path.join(
        hdf_directory_path,
        "etats_uniques",
        )


def clean_law():
    """ Extract relevant data from grille and change to convenient dtype then save to HDFStore.
    Returns stored DataFrame"""

    law_xls_path = os.path.join(
        asset_path,
        "neg_pour_ipp.txt")
    law = pd.read_table(law_xls_path)
    law = law[['date_effet_grille', 'ib', 'code_grade_NETNEH', 'echelon']].copy()
    law['date_effet_grille'] = pd.to_datetime(law['date_effet_grille'])
    law['ib'] = law['ib'].fillna(-1)
    law['ib'] = law['ib'].astype('int32')
    law['code_grade_NETNEH'] = law['code_grade_NETNEH'].astype('str')
    law = law[~law['ib'].isin([-1, 0])].copy()
    law.to_hdf(carrieres_a_lier_file_path, 'grilles', format = 'table', data_columns = True, mode = 'w')
    return law


def get_careers_for_which_we_have_law(start_year = 2009):
    """Get carrer data (id, annee, grade, ib) of ids which:
      - grade is present in legislation data at least for one year (freq of grade)
      - year > 2009
      - trimesre == 1
      - ib < 2016, != -1, != 0, != NaN
     Save to HDFStore
     Returns stored DataFrame
     TODO: passer en trimestriel et rajouter etat
     """
    law = pd.read_hdf(carrieres_a_lier_file_path, 'grilles')
    store_carriere = pd.HDFStore(hdf5_file_path)
    codes_grades_NEG_in_law = law.code_grade_NETNEH.unique()
    valid_grades = store_carriere.select(
        'c_netneh',
        where = 'c_netneh in codes_grades_NEG_in_law',
        stop = debug_chunk_size,
        )
    ident_connus = valid_grades.ident.unique()
    condition = "(annee > {}) & (ident in ident_connus) & (ib_ < 1016)".format(start_year)
    valid_ib = store_carriere.select('ib_', where = condition)
    # l'IB annuel va être l'IB du premier semestre dans ce cas, par convention
    careers = valid_ib.merge(valid_grades, on = ['ident', 'annee'], how = 'outer')
    careers = careers[~careers['ib_'].isin([-1, 0])]
    careers = careers[careers['ib_'].notnull()]
    careers['ib_'] = careers['ib_'].astype('int')
    careers = careers[careers['c_netneh'].notnull()]
    careers['annee'] = careers['annee'].astype('str').map(lambda x: str(x)[:4])
    careers['annee'] = pd.to_datetime(careers['annee'])
    print careers
    careers.to_hdf(
        carrieres_a_lier_file_path, ## changer le chemin
        'carrieres_a_lier_1950_1959_1',
        format = 'table',
        data_columns = True,
        )
    return careers


def find_grille_en_effet_indiv(c_netneh, annee):
    """ Pour chaque c_grade_netneh unique et pour chaque annee de 2010 à 2014, trouver la date d'effet de la grille
    qui s'applique et stocker cette date et l'identifiant associé aux c_grade_netneh unique pour chaque annees dans le
    df effectifs_par_grades_annees """
    carrieres_a_lier = pd.HDFStore(carrieres_a_lier_file_path)
    law_grade = carrieres_a_lier.select('grilles', where='code_grade_NETNEH = c_netneh')
    dates = law_grade['date_effet_grille']
    dates = dates[dates < datetime.strptime(annee, '%Y-%m-%d')]
    if dates.empty:
        date = pd.NaT
    else:
        date = str(dates.max())
        date = datetime.strptime(date[:10], "%Y-%m-%d")
    return date


def etats_uniques():
    """ identifier les etats de carrieres uniques, cad les triplets uniques codes grades NETNEH, annee, ib"""
    carrieres_a_lier = pd.HDFStore(carrieres_a_lier_file_path)
    careers = carrieres_a_lier.select('carrieres_a_lier_1950_1959_1')
    etats_uniques = careers.groupby(['annee', 'trimestre', 'c_netneh', 'ib_']).size().reset_index()[['annee', 'trimestre', 'c_netneh', 'ib_']]
    etats_uniques['annee'] = [str(annee)[:4] for annee in etats_uniques['annee']]
    print etats_uniques
    etats_uniques.to_hdf(etats_uniques_file_path, 'etats_uniques_1950_1959_1', format = 'table', data_columns = True)
    return etats_uniques


def append_date_effet_grille_to_etats_uniques_bis():
    from fonction_publique.career_simulation_vectorized import _set_dates_effet

    with pd.HDFStore(etats_uniques_file_path) as store:
        etats_uniques_table = store.select('etats_uniques_1950_1959_1').copy()
        dataframe = etats_uniques_table[['c_netneh', 'annee', 'trimestre']]
        dataframe['year'] = dataframe.annee.astype('int')
        dataframe['month'] = (dataframe.trimestre - 1) * 3 + 1
        dataframe['day'] = 1
        dataframe['observation_date'] = dataframe[['year', 'month', 'day']].apply(lambda s : datetime(*s),axis = 1)
        dataframe.columns = ['grade', 'annee', 'trimestre', 'year', 'month', 'day', 'period']
        carrieres_a_lier = pd.HDFStore(carrieres_a_lier_file_path)
        grilles = carrieres_a_lier.select('grilles')
        _set_dates_effet(dataframe, date_observation = 'period', start_variable_name = 'date_effet_grille',
                next_variable_name = None, grille = grilles)
        dataframe['date_effet_grille'] = dataframe.date_effet_grille
        dataframe.to_hdf(etats_uniques_file_path,
            'etats_uniques_date_effet_1950_1959_1',
            format = 'table',
            data_columns = True)
        return dataframe

#def append_date_effet_grille_to_etats_uniques():
#    """ ajouter les dates d'effets aux états uniques de carrières """
##    etats_uniques = pd.HDFStore('etats_uniques')
##    etats_uniques_table = etats_uniques.select('etats_uniques_1950_1959_1').copy()
#    dates_effet_grille = []
#    with pd.HDFStore(etats_uniques_file_path) as store:
#        etats_uniques_table = store.select('etats_uniques_1950_1959_1').copy()
#        for etat in range(0, len(etats_uniques_table)):
#            print etat
#            c_netneh = etats_uniques_table['c_netneh'][etat]
#            annees = etats_uniques_table['annee'][etat]
#            date_effet_grille = find_grille_en_effet_indiv(c_netneh, annees)
#            dates_effet_grille.append(date_effet_grille)
##    etats_uniques_table['date_effet_grille'] = dates_effet_grille
##    etats_uniques_table.to_hdf('etats_uniques', 'etats_uniques_with_date_effet_1950_1959_1',
##                               format = 'table', data_columns = True)
#    return dates_effet_grille

# fusionné à la main avec les états uniques pour donner le fichier etats_uniques_avec_dates_effets_1950_1959_1
# TO DO BELOW


def merge_date_effet_grille_with_careers():
    """ ajouter les dates d'effets de grilles aux carrieres """
    etats_uniques = pd.HDFStore(etats_uniques_file_path)
    etats_uniques_avec_date_effet = etats_uniques.select('etats_uniques_date_effet_1950_1959_1')
    carrieres_a_lier = pd.HDFStore(carrieres_a_lier_file_path)
    print etats_uniques_avec_date_effet.columns

    carrieres_a_lier['year'] = dataframe.annee.astype('int')
    dataframe['month'] = (dataframe.trimestre - 1) * 3 + 1
    dataframe['day'] = 1
    dataframe['observation_date'] = dataframe[['year', 'month', 'day']].apply(lambda s : datetime(*s),axis = 1)

    carrieres = carrieres_a_lier.select('carrieres_a_lier_1950_1959_1')
    carrieres.columns = ['ident', 'ib_', 'trimestre', 'annee', 'grade']
    carrieres['annee'] = [str(annee)[:10] for annee in carrieres['annee']]
    carrieres_avec_date_effet_grilles = etats_uniques_avec_date_effet.merge(
        carrieres,
        on = ['period', 'grade', 'trimestre'],
        how = 'outer'
        )
#    carrieres_avec_date_effet_grilles.to_hdf(
#        carrieres_a_lier_file_path,
#        'carrieres_avec_date_effet_grilles',
#        format = 'table',
#        data_columns = True,
#        )
    return carrieres_avec_date_effet_grilles


def merge_careers_with_legislation():
    """ ajouter les echelons aux carrieres """
    carrieres_a_lier = pd.HDFStore(carrieres_a_lier_file_path)
    carrieres_avec_date_effet_grilles = carrieres_a_lier.select('carrieres_avec_date_effet_grilles')
    carrieres_avec_date_effet_grilles.columns = ['annee', 'code_grade_NETNEH', 'ib', 'date_effet_grille', 'ident']
    carrieres_avec_date_effet_grilles['date_effet_grille'] = [
        str(annee)[:10] for annee in carrieres_avec_date_effet_grilles['date_effet_grille']
        ]
    law['date_effet_grille'] = [str(annee)[:10] for annee in law['date_effet_grille']]
    carrieres_with_echelon = carrieres_avec_date_effet_grilles.merge(
        law,
        on = ['code_grade_NETNEH', 'date_effet_grille', 'ib'],
        how = 'outer'
        )
#   carrieres_with_echelon.to_hdf('carrieres_a_lier', 'carrieres_with_echelon', format = 'table', data_columns = True)
    return carrieres_with_echelon

# # DO DESCRIPTION DE LA BASE MERGEE
# carrieres_a_lier = pd.HDFStore('carrieres_a_lier')
# carrieres_with_echelon = carrieres_a_lier.select('carrieres_with_echelon')
# carrieres_with_echelon[carrieres_with_echelon['date_effet_grille'] == 'Not_found']
# carrieres_wechelon_cleaned = carrieres_with_echelon[~carrieres_with_echelon['date_effet_grille'].isnull()]
# carrieres_wechelon_cleaned = carrieres_with_echelon[~carrieres_with_echelon['echelon'].isnull()]


def nb_de_grades_uniques_par_agent_2010_2014(unique):
    if unique:
        bim
        car = carrieres_wechelon_cleaned.groupby(['ident'])['code_grade_NETNEH'].unique().reset_index()
        car.columns = ['ident', 'career_netneh']
        career_netneh_length = [len(career) for career in car['career_netneh']]
        car['career_netneh_length'] = career_netneh_length
        career_netneh_uniques = [list(x) for x in set(tuple(x) for x in car['career_netneh'])]

        return car.career_netneh_length.value_counts(dropna = False)
    else:
        car = carrieres_wechelon_cleaned.groupby(['ident'])['code_grade_NETNEH'].size().reset_index()
        car.columns = ['ident', 'career_netneh']
        print car

        return


#if __name__ == '__main__':
   #clean_law()
   # get_careers_for_which_we_have_law(start_year = 2009)
