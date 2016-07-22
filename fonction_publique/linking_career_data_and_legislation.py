# -*- coding:utf-8 -*-


from __future__ import division
import os
import pandas as pd
from datetime import datetime

from fonction_publique.base import asset_path, hdf_directory_path, hdf5_file_path, DEBUG, debug_chunk_size

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
    """ Extract relevant data from grille and change to convenient dtype then save to HDFStore."""

    law_xls_path = os.path.join(
        asset_path,
        "neg_pour_ipp.txt")
    law = pd.read_table(law_xls_path)
    law = law[['date_effet_grille', 'ib', 'code_grade_NETNEH', 'echelon', 'max_mois', 'min_mois', 'moy_mois']].copy()

    law['date_effet_grille'] = pd.to_datetime(law.date_effet_grille)

    for variable in ['ib', 'max_mois', 'min_mois', 'moy_mois']:
        law[variable] = law[variable].fillna(-1).astype('int32')

    law['code_grade_NETNEH'] = law['code_grade_NETNEH'].astype('str')

    law = law[~law['ib'].isin([-1, 0])].copy()
    law.to_hdf(carrieres_a_lier_file_path, 'grilles', format = 'table', data_columns = True, mode = 'w')


def get_careers_for_which_we_have_law(start_year = 2009):
    """Get carrer data (id, annee, grade, ib) of ids which:
      - grade is present in legislation data at least for one year (freq of grade)
      - year > 2009
      - ib < 2016, != -1, != 0, != NaN
     Save to HDFStore
     Returns stored DataFrame
     """
    law = pd.read_hdf(carrieres_a_lier_file_path, 'grilles')
    store_carriere = pd.HDFStore(hdf5_file_path)
    codes_grades_NETNEH_in_law = law.code_grade_NETNEH.unique()
    valid_grades = store_carriere.select(
        'c_netneh',
        where = 'c_netneh in codes_grades_NETNEH_in_law',
        stop = debug_chunk_size,
        )
    ident_connus = valid_grades.ident.unique()
    condition = "(annee > {}) & (ident in ident_connus) & (ib_ < 1016)".format(start_year)
    valid_ib = store_carriere.select('ib_', where = condition)
    careers = valid_ib.merge(valid_grades, on = ['ident', 'annee'], how = 'outer')
    careers = careers[~careers['ib_'].isin([-1, 0])]
    careers = careers[careers['ib_'].notnull()]
    careers['ib_'] = careers['ib_'].astype('int')
    careers = careers[careers['c_netneh'].notnull()]
    careers['annee'] = careers['annee'].astype('str').map(lambda x: str(x)[:4])
    careers['annee'] = pd.to_datetime(careers['annee'])
    assert not careers.empty, 'careers is an empty DataFrame'
    careers.to_hdf(
        carrieres_a_lier_file_path,
        'carrieres_a_lier_1950_1959_1',
        format = 'table',
        data_columns = True,
        )
    print careers


def etats_uniques():
    """ identifier les etats de carrieres uniques, cad les triplets uniques codes grades NETNEH, annee, ib"""

    carrieres_a_lier = pd.HDFStore(carrieres_a_lier_file_path)
    print carrieres_a_lier
    careers = carrieres_a_lier.select('carrieres_a_lier_1950_1959_1')
    etats_uniques = careers.groupby(['annee', 'trimestre', 'c_netneh', 'ib_']).size().reset_index()[[
        'annee',
        'trimestre',
        'c_netneh',
        'ib_']]
    etats_uniques['annee'] = [str(annee)[:4] for annee in etats_uniques['annee']]
    etats_uniques.to_hdf(etats_uniques_file_path, 'etats_uniques_1950_1959_1', format = 'table', data_columns = True)


def append_date_effet_grille_to_etats_uniques_bis():
    from fonction_publique.career_simulation_vectorized import _set_dates_effet

    with pd.HDFStore(etats_uniques_file_path) as store:
        etats_uniques_table = store.select('etats_uniques_1950_1959_1').copy()
        dataframe = etats_uniques_table[['c_netneh', 'annee', 'trimestre']]
        dataframe['year'] = dataframe.annee
        dataframe['month'] = (dataframe.trimestre - 1) * 3 + 1
        dataframe['day'] = 1
        dataframe['observation_date'] = pd.to_datetime(dataframe[['year', 'month', 'day']])
        dataframe.columns = ['grade', 'annee', 'trimestre', 'year', 'month', 'day', 'period']
        dataframe = dataframe[['grade', 'annee', 'trimestre', 'period']]
        carrieres_a_lier = pd.HDFStore(carrieres_a_lier_file_path)
        grilles = carrieres_a_lier.select('grilles')
        grilles = grilles.rename(columns = dict(code_grade_NETNEH = 'code_grade'))
        _set_dates_effet(
            dataframe,
            date_observation = 'period',
            start_variable_name = 'date_effet_grille',
            next_variable_name = None,
            grille = grilles)
        dataframe.to_hdf(etats_uniques_file_path,
            'etats_uniques_date_effet_1950_1959_1',
            format = 'table',
            data_columns = True)


def merge_date_effet_grille_with_careers():
    """ ajouter les dates d'effets de grilles aux carrieres """

    etats_uniques = pd.HDFStore(etats_uniques_file_path)
    etats_uniques_avec_date_effet = etats_uniques.select('etats_uniques_date_effet_1950_1959_1')
    carrieres_a_lier = pd.HDFStore(carrieres_a_lier_file_path)
    carrieres = carrieres_a_lier.select('carrieres_a_lier_1950_1959_1')
    carrieres['annee'] = [str(annee)[:4] for annee in carrieres['annee']]
    carrieres['year'] = carrieres.annee.astype('int')
    carrieres['month'] = (carrieres.trimestre - 1) * 3 + 1
    carrieres['day'] = 1
    carrieres['period'] = pd.to_datetime(carrieres[['year', 'month', 'day']])
    carrieres.columns = ['ident', 'ib_', 'trimestre', 'annee', 'grade', 'year', 'month', 'day', 'period']
    carrieres = carrieres[['ident', 'ib_', 'trimestre', 'grade', 'period']]
    carrieres_avec_date_effet_grilles = etats_uniques_avec_date_effet.merge(
        carrieres,
        on = ['period', 'grade', 'trimestre'],
        how = 'outer'
        )
    carrieres_avec_date_effet_grilles.to_hdf(
        carrieres_a_lier_file_path,
        'carrieres_avec_date_effet_grilles',
        format = 'table',
        data_columns = True,
        )


def merge_careers_with_legislation():
    """ ajouter les echelons aux carrieres """

    law = pd.read_hdf(carrieres_a_lier_file_path, 'grilles')
    carrieres_a_lier = pd.HDFStore(carrieres_a_lier_file_path)
    carrieres_avec_date_effet_grilles = carrieres_a_lier.select('carrieres_avec_date_effet_grilles')
    carrieres_avec_date_effet_grilles = carrieres_avec_date_effet_grilles[[
        'grade',
        'trimestre',
        'period',
        'date_effet_grille',
        'ident',
        'ib_'
        ]]
    carrieres_avec_date_effet_grilles.columns = [
        'code_grade_NETNEH',
        'trimestre',
        'period',
        'date_effet_grille',
        'ident',
        'ib'
        ]
    law['date_effet_grille'] = [str(annee)[:10] for annee in law['date_effet_grille']]
    law['date_effet_grille'] = pd.to_datetime(law.date_effet_grille)
    carrieres_with_echelon = carrieres_avec_date_effet_grilles.merge(
        law,
        on = ['code_grade_NETNEH', 'date_effet_grille', 'ib'],
        how = 'outer'
        )
    carrieres_with_echelon.to_hdf(
        carrieres_a_lier_file_path,
        'carrieres_with_echelon',
        format = 'table',
        data_columns = True,
        )


if __name__ == '__main__':
    clean_law()
    get_careers_for_which_we_have_law(start_year = 2009)
    etats_uniques()
    append_date_effet_grille_to_etats_uniques_bis()
    merge_date_effet_grille_with_careers()
    merge_careers_with_legislation()
