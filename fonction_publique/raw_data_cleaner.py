# -*- coding:utf-8 -*-


from __future__ import division


import gc
import logging
import os

import pandas as pd

from fonction_publique.base import DEFAULT_CHUNKSIZE, get_careers_hdf_path, timing

log = logging.getLogger(__name__)


@timing
def get_subset(variable = None, stata_file_path = None, debug = False, chunksize = None):
    """ selectionne le sous-dataframe pour une variable, appelee variable ici"""
    if debug is True:
        assert (type(chunksize) == int) and (chunksize > 0), "chunksize = {}".format(chunksize)
    else:
        assert chunksize is None
    if chunksize is None:
        chunksize = DEFAULT_CHUNKSIZE
    log.info('getting variable {} from {}'.format(variable, stata_file_path))
    reader = pd.read_stata(stata_file_path, chunksize = chunksize)
    result = pd.DataFrame()
    selected_columns = None
    for chunk in reader:
        if selected_columns is None:
            # variable and column name may mismatch: ib vs ib_*, etc
            columns = chunk.columns.tolist()
            selected_columns = [column for column in columns if (variable in column)]
        #
        result = result.append(chunk[selected_columns + ['ident']])
        if debug:
            break
    gc.collect()
    return result


@timing
def clean_subset(variable = None, years_range = None, quarterly = False, stata_file_path = None, debug = False,
         chunksize = None):
    """ nettoie chaque variable pour en faire une dataframe propre """
    subset_result = pd.DataFrame()
    subset = get_subset(variable, stata_file_path, debug, chunksize = chunksize)
    # Build a hierarchical index as in
    # http://stackoverflow.com/questions/17819119/coverting-index-into-multiindex-hierachical-index-in-pandas
    for annee in years_range:
        if quarterly:
            for quarter in range(1, 5):
                if variable == 'ib_':
                    subset_cleaned = subset[['ident', '{}{}_{}'.format(variable, annee, quarter)]].copy()
                    subset_cleaned.rename(
                        columns = {'{}{}_{}'.format(variable, annee, quarter): variable},
                        inplace = True
                        )
                else:
                    subset_cleaned = subset[['ident', '{}_{}_{}'.format(variable, annee, quarter)]].copy()
                    subset_cleaned.rename(
                        columns = {'{}_{}_{}'.format(variable, annee, quarter): variable},
                        inplace = True
                        )
                #
                subset_cleaned['trimestre'] = quarter
                subset_cleaned['annee'] = annee
                subset_result = pd.concat([subset_result, subset_cleaned])
        #
        else:
            subset_cleaned = subset[['ident', '{}_{}'.format(variable, annee)]].copy()
            subset_cleaned.rename(columns = {'{}_{}'.format(variable, annee): variable}, inplace = True)
            subset_cleaned['annee'] = annee
            subset_result = pd.concat([subset_result, subset_cleaned])

    gc.collect()
    return subset_result


@timing
def format_columns(variable = None, years_range = None, quarterly = False, clean_directory_path = None,
        stata_file_path = None, debug = False, chunksize = None):
    log.info('formatting column {}'.format(variable))
    subset_to_format = clean_subset(variable, years_range, quarterly, stata_file_path, debug = debug,
        chunksize = chunksize)
    # dtype format
    # always format ident
    subset_to_format.ident = subset_to_format.ident.astype('int32')
    subset_to_format.annee = subset_to_format.annee.astype('int16')
    if variable in ['qualite', 'statut', 'etat_']:
        subset_to_format[variable] = subset_to_format[variable].astype('category')
    elif variable in ['ib_']:
        subset_to_format['ib_'].fillna(-1, inplace = True)
        subset_to_format['ib'] = subset_to_format['ib_'].astype('int32')
        variable = 'ib'
        del subset_to_format['ib_']
    else:
        subset_to_format[variable] = subset_to_format[variable].astype('str')

    careers_hdf_path = get_careers_hdf_path(clean_directory_path, stata_file_path, debug)

    subset_to_format.to_hdf(
        careers_hdf_path, '{}'.format(variable), format = 'table', data_columns = True
        )


def format_generation(stata_file_path, clean_directory_path = None, debug = False, chunksize = None):
    log.info('formatting generation')
    generation = get_subset('generation', stata_file_path, debug = debug, chunksize = chunksize)
    generation.ident = generation.ident.astype('int')
    generation.generation = generation.generation.astype('int32')
    careers_hdf_path = get_careers_hdf_path(clean_directory_path, stata_file_path, debug)
    if not os.path.exists(os.path.dirname(careers_hdf_path)):
        log.info('{} is not a valid path. Creating it'.format(os.path.dirname(careers_hdf_path)))
        os.makedirs(os.path.dirname(careers_hdf_path))
    generation.to_hdf(careers_hdf_path, 'generation', format = 'table', data_columns = True)
    log.info('generation was added to carriere')


def main(raw_directory_path = None, clean_directory_path = None, debug = None, chunksize = None):
    assert raw_directory_path is not None
    arg_format_columns = [
        dict(
            variable = 'c_netneh',
            years_range = range(2010, 2015),
            quarterly = False,
            ),
        dict(
            variable = 'c_cir',
            years_range = range(2010, 2015),
            quarterly = False,
            ),
        dict(
            variable = 'libemploi',
            years_range = range(2000, 2015),
            quarterly = False,
            ),
        # should contain _ otherwise libemploi which contains 'ib' would also selected
        dict(
            variable = 'ib_',
            years_range = range(1970, 2015),
            quarterly = True,
            ),
        dict(
            variable = 'qualite',
            years_range = range(1970, 2015),
            quarterly = False,
            ),
        dict(
            variable = 'statut',
            years_range = range(1970, 2015),
            quarterly = False,
            ),
        dict(
            variable = 'etat',
            years_range = range(1970, 2015),
            quarterly = True,
            ),
        ]

    for stata_file in os.listdir(raw_directory_path):
        if not stata_file.endswith('.dta'):
            continue
        stata_file_path = os.path.join(raw_directory_path, '{}'.format(stata_file))
        log.info('Processing {}'.format(stata_file_path))
        format_generation(
            stata_file_path,
            clean_directory_path = clean_directory_path,
            debug = debug,
            chunksize = chunksize,
            )
        for kwargs in arg_format_columns:
            kwargs.update(dict(
                clean_directory_path = clean_directory_path,
                stata_file_path = stata_file_path,
                debug = debug,
                chunksize = chunksize,
                ))
            format_columns(**kwargs)
