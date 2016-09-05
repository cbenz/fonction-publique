# -*- coding:utf-8 -*-


from __future__ import division
from datetime import datetime
from fonction_publique.base import law_xls_path, law_hdf_path, get_careers_hdf_path, get_tmp_hdf_path, \
    debug_chunk_size, DEBUG_CLEAN_CARRIERES, get_output_hdf_path, raw_directory_path, clean_directory_path
from fonction_publique.career_simulation_vectorized import _set_dates_effet
import logging
import os
import pandas as pd

log = logging.getLogger(__name__)


def law_to_hdf():
    """ Extract relevant data from grille and change to convenient dtype then save to HDFStore."""
    law = pd.read_table(law_xls_path)
    law = law[['date_effet_grille', 'ib', 'code_grade_NETNEH', 'echelon', 'max_mois', 'min_mois', 'moy_mois']].copy()
    law['date_effet_grille'] = pd.to_datetime(law.date_effet_grille)
    for variable in ['ib', 'max_mois', 'min_mois', 'moy_mois']:
        law[variable] = law[variable].fillna(-1).astype('int32')
    law['code_grade'] = law['code_grade_NETNEH'].astype('str')
    law = law[~law['ib'].isin([-1, 0])].copy()
    law.to_hdf(law_hdf_path, 'grilles', format = 'table', data_columns = True, mode = 'w')
    return law.head()


def get_careers_for_which_we_have_law(start_year = 2009, stata_file_path = None):
    """Get carrer data (id, annee, grade, ib) of ids which:
      - grade is present in legislation data at least for one year (freq of grade)
      - year > 2009
      - ib < 2016, != -1, != 0, != NaN
     Save to HDFStore
     Returns stored DataFrame
     """
    law = pd.read_hdf(law_hdf_path, 'grilles')
    careers_hdf_path = get_careers_hdf_path(clean_directory_path = clean_directory_path,
        stata_file_path = stata_file_path, debug = DEBUG_CLEAN_CARRIERES)
    careers_hdf = pd.HDFStore(careers_hdf_path)
    grades_in_law = law.code_grade.unique()
    valid_grades = careers_hdf.select(
        'c_netneh',
        where = 'c_netneh in grades_in_law',
        stop = debug_chunk_size,
        )
    valid_idents = valid_grades.ident.unique()
    condition = "annee > {} & ident in valid_idents & ib < 1016".format(start_year)
    valid_ib = careers_hdf.select('ib', where = condition)
    careers = valid_ib.merge(valid_grades, on = ['ident', 'annee'], how = 'outer')
    careers = careers[~careers['ib'].isin([-1, 0])]
    careers = careers[careers['ib'].notnull()]
    careers['ib'] = careers['ib'].astype('int')
    careers = careers[careers['c_netneh'].notnull()]

    careers['annee'] = careers['annee'].astype('str').map(lambda x: str(x)[:4])
    careers['annee'] = pd.to_datetime(careers['annee'])
    assert not careers.empty, 'careers is an empty DataFrame'
    tmp_hdf_path = get_tmp_hdf_path(stata_file_path, debug = DEBUG_CLEAN_CARRIERES)
    assert os.path.exists(os.path.dirname(tmp_hdf_path)), 'Invalid path {}'.format(os.path.dirname(tmp_hdf_path))
    careers.to_hdf(
        tmp_hdf_path,
        'tmp_1',
        format = 'table',
        data_columns = True,
        )


def get_unique_career_states(stata_file_path = None):
    """ identifier les etats de carrieres uniques, cad les triplets uniques codes grades NETNEH, annee, ib"""
    tmp_hdf_path = get_tmp_hdf_path(stata_file_path, debug = DEBUG_CLEAN_CARRIERES)
    tmp_hdf = pd.HDFStore(tmp_hdf_path)
    careers = tmp_hdf.select('tmp_1')
    careers = careers[['annee', 'trimestre', 'c_netneh']]
    unique_career_states = careers.groupby(['annee', 'trimestre', 'c_netneh']).size().reset_index()[[
        'annee',
        'trimestre',
        'c_netneh',
        ]]
    unique_career_states['annee'] = [str(annee)[:4] for annee in unique_career_states['annee']]
    unique_career_states.to_hdf(tmp_hdf_path, 'tmp_2', format = 'table', data_columns = True)


def append_date_effet_to_unique_career_states(stata_file_path = None):
    tmp_hdf_path = get_tmp_hdf_path(stata_file_path, debug = DEBUG_CLEAN_CARRIERES)
    tmp_hdf = pd.HDFStore(tmp_hdf_path)
    law = pd.HDFStore(law_hdf_path)
    with tmp_hdf as store:
        unique_career_states = store.select('tmp_2').copy()
        dataframe = unique_career_states[['c_netneh', 'annee', 'trimestre']].copy()

        assert not dataframe.duplicated().any(), 'There are duplicatd row in dataframe'
        dataframe['year'] = dataframe.annee
        dataframe['month'] = (dataframe.trimestre - 1) * 3 + 1
        dataframe['day'] = 1
        dataframe['observation_date'] = pd.to_datetime(dataframe[['year', 'month', 'day']])
        assert not dataframe.duplicated().any(), 'There are duplicatd row in dataframe'
        dataframe.columns = ['grade', 'annee', 'trimestre', 'year', 'month', 'day', 'period']  # TODO use rename like below
        dataframe = dataframe[['grade', 'annee', 'trimestre', 'period']].copy()
        assert not dataframe.duplicated().any(), 'There are duplicatd row in dataframe'
        careers = store.select('tmp_1')
        assert not careers.duplicated().any(), 'There are duplicatd row in careers'
        grilles = law.select('grilles')
        grilles = grilles.rename(columns = dict(code_grade_NETNEH = 'grade'))
        _set_dates_effet(
            dataframe,
            date_observation = 'period',
            start_variable_name = 'date_effet_grille',
            next_variable_name = None,
            grille = grilles)
        assert not dataframe.duplicated().any(), 'There are duplicatd row in unique_career_states (tmp_3)'
        dataframe.to_hdf(tmp_hdf_path,
            'tmp_3',
            format = 'table',
            data_columns = True)


def merge_date_effet_grille_with_careers(stata_file_path = None):
    """ ajouter les dates d'effets de grilles aux carrieres """
    tmp_hdf_path = get_tmp_hdf_path(stata_file_path, debug = DEBUG_CLEAN_CARRIERES)
    tmp_hdf = pd.HDFStore(tmp_hdf_path)
    unique_career_states = tmp_hdf.select('tmp_3')

    assert not unique_career_states.duplicated().any(), 'There are duplicatd row in unique_career_states'
    careers = tmp_hdf.select('tmp_1')

    careers['annee'] = [str(annee)[:4] for annee in careers['annee']]
    careers['year'] = careers.annee.astype('int')
    careers['month'] = (careers.trimestre - 1) * 3 + 1
    careers['day'] = 1
    careers['period'] = pd.to_datetime(careers[['year', 'month', 'day']])
    careers = careers[['ident', 'ib', 'trimestre', 'c_netneh', 'period']].copy()
    careers.columns = ['ident', 'ib', 'trimestre', 'grade', 'period']
    careers.rename(columns = dict(c_netneh = 'grade'), inplace = True)
    assert not careers.duplicated().any(), 'There are duplicatd row in careers'
    assert not unique_career_states.duplicated().any(), 'There are duplicatd row in unique_career_states'
    careers = unique_career_states.merge(
        careers,
        on = ['period', 'grade', 'trimestre'],
        how = 'outer'
        )
    assert not careers.duplicated().any(), 'There are duplicatd row in careers'
    careers.to_hdf(
        tmp_hdf_path,
        'tmp_4',
        format = 'table',
        data_columns = True,
        )


def merge_careers_with_legislation(stata_file_path = None):
    """ ajouter les echelons aux carrieres """
    tmp_hdf_path = get_tmp_hdf_path(stata_file_path, debug = DEBUG_CLEAN_CARRIERES)
    tmp_hdf = pd.HDFStore(tmp_hdf_path)
    law = pd.HDFStore(law_hdf_path)
    grilles = law.select('grilles')

    careers = tmp_hdf.select('tmp_4')
    assert not careers.duplicated().any(), 'There are duplicatd row in careers'
    careers = careers[[
        'grade',
        'trimestre',
        'period',
        'date_effet_grille',
        'ident',
        'ib'
        ]].copy()
    careers.rename(columns = dict(grade = 'code_grade_NETNEH'), inplace = True)
    assert not careers.duplicated().any(), 'There are duplicatd row in careers'
    grilles['date_effet_grille'] = [str(annee)[:10] for annee in grilles['date_effet_grille']]
    grilles['date_effet_grille'] = pd.to_datetime(grilles.date_effet_grille)
    careers = careers.merge(
        grilles,
        on = ['code_grade_NETNEH', 'date_effet_grille', 'ib'],
        how = 'outer'
        )
    assert not careers.duplicated().any(), 'There are duplicatd row in careers (after merge)'
    careers.to_hdf(
        tmp_hdf_path,
        'tmp_5',
        format = 'table',
        data_columns = True,
        )


def merge_careers_with_echelon_with_etat(stata_file_path = None):
    tmp_hdf_path = get_tmp_hdf_path(stata_file_path, debug = DEBUG_CLEAN_CARRIERES)
    tmp_hdf = pd.HDFStore(tmp_hdf_path)
    clean_hdf_path = get_careers_hdf_path(clean_directory_path = clean_directory_path,
        stata_file_path = stata_file_path, debug = DEBUG_CLEAN_CARRIERES)
    clean_hdf = pd.HDFStore(clean_hdf_path)
    table_var_etat = clean_hdf.select('etat', where = 'annee > 2009')
    table_var_etat = table_var_etat[~table_var_etat['ident'].isnull()]
    table_var_etat['ident'] = table_var_etat['ident'].astype(int)
    careers = tmp_hdf.select('tmp_5')
    careers = careers[~careers['ident'].isnull()]
    careers['ident'] = careers['ident'].astype(int)
    careers['trimestre'] = careers['trimestre'].astype(int)

    careers['annee'] = careers.period.dt.year
    careers = careers.merge(table_var_etat, on = ['ident', 'annee', 'trimestre'], how = 'outer')
    careers = careers[~careers['echelon'].isnull()]
    output_hdf_path = get_output_hdf_path(stata_file_path, debug = DEBUG_CLEAN_CARRIERES)
    assert os.path.exists(os.path.dirname(output_hdf_path)), '{} is not a valid path'.format(
        os.path.dirname(output_hdf_path))
    assert not careers.duplicated().any(), 'There are duplicatd row in careers'
    careers.to_hdf(output_hdf_path, 'output', format = 'table', data_columns = True)
    return careers

#if __name__ == '__main__':
#    law_to_hdf()
#    for stata_file in os.listdir(raw_directory_path):
#        get_careers_for_which_we_have_law(start_year = 2009, stata_file_path = stata_file)
#        get_unique_career_states(stata_file_path = stata_file)
#        append_date_effet_to_unique_career_states(stata_file_path = stata_file)
#        merge_date_effet_grille_with_careers(stata_file_path = stata_file)
#        merge_careers_with_legislation(stata_file_path = stata_file)
#        merge_careers_with_echelon_with_etat(stata_file_path = stata_file)
#        break
