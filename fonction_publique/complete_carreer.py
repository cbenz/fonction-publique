# -*- coding:utf-8 -*-


from __future__ import division
import logging
import pandas as pd

from fonction_publique.base import get_output_hdf_path, law_hdf_path, DEBUG

from fonction_publique.career_simulation_vectorized import AgentFpt


log = logging.getLogger(__name__)


def temporary_clean_echelon(dataframe):
    dataframe.echelon = pd.to_numeric(dataframe.echelon, errors = 'coerce')
    dataframe = dataframe[dataframe.echelon.notnull()].copy()
    dataframe['echelon'] = dataframe.echelon.astype('int32')
    return dataframe


def extract_initial(file_path, debug = None):
    careers_file_path = get_output_hdf_path(file_path = file_path, debug = debug)
    careers = pd.read_hdf(careers_file_path, 'output')
    careers = careers.dropna(subset = ['echelon'])
    careers = careers.dropna(subset = ['ident'])
    careers = temporary_clean_echelon(careers)
    assert careers.ident.notnull().all()
    if careers.duplicated().sum():  # change this to assert
        log.info('the following are duplicated careers: \n {}'.format(careers[careers.duplicated()]))
        log.info('We drop the duplicated careers')
        careers = careers.drop_duplicates()

    careers.reset_index(inplace = True)
    starting_careers = careers.iloc[careers.groupby('ident')['period'].idxmin().values.ravel()]
    log.info(starting_careers.head())
    starting_careers = starting_careers.rename(columns = dict(code_grade_NETNEH = 'grade'))

    law_store = pd.HDFStore(law_hdf_path)
    grilles = law_store.select('grilles')
    grilles = grilles[
        (grilles.max_mois > 0)  # TODO: add other conditions
        ]
    grilles = temporary_clean_echelon(grilles)
    print grilles.dtypes
    print grilles.echelon.value_counts(dropna = False)
    print grilles.head()

    agents = AgentFpt(
        starting_careers[['ident', 'period', 'grade', 'echelon']].copy(),
        grille = grilles)
    print agents.dataframe
    print agents.compute_result()
    return agents.result


if __name__ == '__main__':
    result = extract_initial(
        file_path = 'c_g1950_g1959.dta',
        debug = DEBUG,
        ).sort_values(['ident', 'echelon', 'quarter'])
