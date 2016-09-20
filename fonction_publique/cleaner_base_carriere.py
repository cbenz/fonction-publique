# -*- coding:utf-8 -*-


from __future__ import division

import logging
import os
import pandas as pd
import time


from fonction_publique.base import get_careers_hdf_path, debug_chunk_size


log = logging.getLogger(__name__)


# Timer
def timing(f):
    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        log.info('%s function took %0.3f s' % (f.func_name, (time2 - time1)))
        return ret
    return wrap


def select_columns(variable = None, stata_file_path = None):
    """ selectionne les noms de colonnes correspondant à la variable (variable) qui nous interesse """
    reader_for_colnames = pd.read_stata(stata_file_path, chunksize = 1)
    for chunk in reader_for_colnames:
        chunk_to_get_colnames = chunk
        break
    colnames = chunk_to_get_colnames.columns.to_series()
    colnames_subset = pd.Series(['ident'])
    colnames_to_keep = colnames.str.contains(variable)
    colnames_kept = colnames[colnames_to_keep]
    colnames_subset = colnames_subset.append(colnames_kept)
    return colnames_subset.reset_index(drop = True)


@timing
def get_subset(variable = None, stata_file_path = None, debug = False):
    """ selectionne le sous-dataframe pour une variable, appelee variable ici"""
    log.info('getting variable {} from {}'.format(variable, stata_file_path))
    if debug:
        reader = pd.read_stata(stata_file_path, chunksize = debug_chunk_size)
    else:
        reader = pd.read_stata(stata_file_path, chunksize = 50000)
    colnames = select_columns(variable, stata_file_path)
    get_subset = pd.DataFrame()
    for chunk in reader:
        subset = chunk[colnames]
        get_subset = get_subset.append(subset)
        if debug:
            break
    return get_subset


@timing
def clean_subset(variable = None, years_range = None, quarterly = False, stata_file_path = None, debug = False):
    """ nettoie chaque variable pour en faire un df propre """
    subset_result = pd.DataFrame()
    subset = get_subset(variable, stata_file_path, debug)
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

    return subset_result


@timing
def format_columns(variable = None, years_range = None, quarterly = False, clean_directory_path = None,
        stata_file_path = None, debug = False):
    log.info('formatting column {}'.format(variable))
    subset_to_format = clean_subset(variable, years_range, quarterly, stata_file_path, debug = debug)
    subset_to_format['ident'] = subset_to_format['ident'].astype('int')
    if variable in ['qualite', 'statut', 'etat_']:
        subset_to_format[variable] = subset_to_format[variable].astype('category')
    elif variable in ['ident', '_netneh', 'cir', 'generation']:
        subset_to_format[variable] = subset_to_format[variable].astype('int')
    elif variable in ['ib_']:
        subset_ib = subset_to_format['ib_'].fillna(-1)
        subset_ib = subset_ib.astype('int32')
        subset_to_format['ib'] = subset_ib
        variable = 'ib'
    else:
        subset_to_format[variable] = subset_to_format[variable].astype('str')

    careers_hdf_path = get_careers_hdf_path(clean_directory_path, stata_file_path, debug)

    subset_to_format.to_hdf(
        careers_hdf_path, '{}'.format(variable), format = 'table', data_columns = True
        )


def format_generation(stata_file_path, clean_directory_path = None, debug = False):
    log.info('formatting generation')
    generation = get_subset('generation', stata_file_path, debug)
    generation['ident'] = generation['ident'].astype('int')
    generation['generation'] = generation['generation'].astype('int32')

    careers_hdf_path = get_careers_hdf_path(clean_directory_path, stata_file_path, debug)
    assert os.path.exists(os.path.dirname(careers_hdf_path)), '{} is not a valid path'.format(careers_hdf_path)
    generation.to_hdf(careers_hdf_path, 'generation', format = 'table', data_columns = True)
    return 'generation was added to base_carriere'


def main(raw_directory_path = None, clean_directory_path = None, debug = None):
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
        format_generation(stata_file_path, clean_directory_path = clean_directory_path, debug = debug)
        for kwargs in arg_format_columns:
            kwargs.update(dict(
                clean_directory_path = clean_directory_path,
                stata_file_path = stata_file_path,
                debug = debug,
                ))
            format_columns(**kwargs)
