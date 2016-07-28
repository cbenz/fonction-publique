# -*- coding:utf-8 -*-


from __future__ import division
import os
import pandas as pd
from datetime import datetime

from fonction_publique.base import asset_path, get_output_hdf_path, law_hdf_path, DEBUG, debug_chunk_size

from fonction_publique.career_simulation_vectorized import AgentFpt


def temporary_clean_echelon(dataframe):
    dataframe.echelon = pd.to_numeric(dataframe.echelon, errors = 'coerce')
    dataframe = dataframe[dataframe.echelon.notnull()].copy()
    dataframe['echelon'] = dataframe.echelon.astype('int32')
    return dataframe


def extract_initial():
    careers_file_path = get_output_hdf_path(stata_file_path = 'c_g1950_g1959.dta', debug_cleaner_base_carriere = DEBUG)
    careers = pd.read_hdf(careers_file_path, 'output')
    # print careers.head()
    # print careers.dtypes
    careers = careers.dropna(subset = ['echelon'])
    careers = careers.dropna(subset = ['ident'])
    careers = temporary_clean_echelon(careers)
    print careers.ident.isnull().sum()
    print careers.head()
    print careers.dtypes
    print 'dup', careers.duplicated().sum()
    print careers[careers.duplicated()]
    careers = careers.drop_duplicates()
    print 'dup', careers.duplicated().sum()
    print careers.head()
    print careers.duplicated(subset = ['ident', 'period']).sum()
    print careers.groupby('ident')['period'].idxmin().values.ravel()
    print len(careers)
    careers.reset_index(inplace = True)
    starting_careers = careers.iloc[careers.groupby('ident')['period'].idxmin().values.ravel()]
    print starting_careers.head()
    starting_careers = starting_careers.rename(columns = dict(code_grade_NETNEH = 'grade'))

    law_store = pd.HDFStore(law_hdf_path)
    grilles = law_store.select('grilles')
    grilles = grilles[
        (grilles.max_mois > 0)  # TODO: add other conditions
        ]
    grilles = temporary_clean_echelon(grilles)
    print grilles.dtypes
    print grilles.echelon.value_counts(dropna = False)
    # grilles = grilles.rename(columns = dict(code_grade_NETNEH = 'code_grade'))
    print grilles.head()

    agents = AgentFpt(
        starting_careers[['ident', 'period', 'grade', 'echelon']].copy(),
        grille = grilles)
    print agents.dataframe
    print agents.compute_result()
    # print agents.result.to_hdf('toto.h5', 'toto', format = 'table', data_columns = True)
    return agents.result

if __name__ == '__main__':
    result = extract_initial().sort_values(['ident', 'echelon', 'quarter'])
    result
