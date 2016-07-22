# -*- coding:utf-8 -*-


from __future__ import division
import os
import pandas as pd
import pylab as plt
import seaborn as sns
import time


from fonction_publique.base import stata_data_path, hdf_directory_path, DEBUG_CLEAN_CARRIERES, hdf5_file_path
stata_file_path = os.path.join(stata_data_path, 'c_g1950_g1959.dta')


# Timer
def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f s' % (f.func_name, (time2 - time1))
        return ret
    return wrap


def select_columns(variable):  # e.g 'ident' 'qualite' 'statut' 'cir' '_netneh' 'libemploi' 'ib_' 'etat_'
    # colnames = read_only_store.select('data', 'index < 2').columns.to_series()
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
def get_subset(variable):
    """ selectionne le sous-dataframe pour une variable, appelee variable ici"""
    reader = pd.read_stata(stata_file_path, chunksize = 50000)
    colnames = select_columns(variable)
    get_subset = pd.DataFrame()
    for chunk in reader:
        subset = chunk[colnames]
        get_subset = get_subset.append(subset)
        if DEBUG_CLEAN_CARRIERES:
            break
    return get_subset


@timing
def clean_subset(variable, period, quarterly):
    """ nettoie chaque variable pour en faire un df propre """
    subset_result = pd.DataFrame()
    subset = get_subset(variable)
    # Build a hierarchical index as in http://stackoverflow.com/questions/17819119/coverting-index-into-multiindex-hierachical-index-in-pandas
    for annee in period:
        if quarterly:
            if variable == 'ib_':
                for quarter in range(1, 5):
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
                subset_cleaned['trimestre'] = quarter
                subset_cleaned['annee'] = annee
                subset_result = pd.concat([subset_result, subset_cleaned])

        else:
            subset_cleaned = subset[['ident', '{}_{}'.format(variable, annee)]].copy()
            subset_cleaned.rename(columns = {'{}_{}'.format(variable, annee): variable}, inplace = True)
            subset_cleaned['annee'] = annee
            subset_result = pd.concat([subset_result, subset_cleaned])

    return subset_result


@timing
def format_columns(variable = None, years_range = None, quarterly = False):

    subset_to_format = clean_subset(variable, years_range, quarterly)
    subset_to_format['ident'] = subset_to_format['ident'].astype('int')
    if variable in ['qualite', 'statut', 'etat_']:
        subset_to_format[variable] = subset_to_format[variable].astype('category')
    elif variable in ['ident', '_netneh', 'cir', 'generation']:
        subset_to_format[variable] = subset_to_format[variable].astype('int')
    elif variable in ['ib_']:
        subset_ib = subset_to_format['ib_'].fillna(-1)
        subset_ib = subset_ib.astype('int32')
        subset_to_format['ib_'] = subset_ib
    else:
        subset_to_format[variable] = subset_to_format[variable].astype('str')

    subset_to_format.to_hdf(hdf5_file_path, '{}'.format(variable), format = 'table', data_columns = True)

    return 'df is cleaned'


def format_generation():
    generation = get_subset('generation')
    generation['ident'] = generation['ident'].astype('int')
    generation['generation'] = generation['generation'].astype('int32')
    generation.to_hdf(hdf5_file_path, 'generation', format = 'table', data_columns = True)
    return 'generation was added to base_carriere'

# def gen_libemploi_2010_2014():
#    """ Cree une table libemploi_2010_2014 p'rovisoire pour comparer le nb de libelles grades sur la periode avec
#    les nb de codes grades sur la periodes. La table libemploi est en effet disponible pour 2000-2014.
#    """
#    df_libemploi = get_df('libemploi')
#    df_libemploi_subset = df_libemploi.to_hdf(hdf5_file_path, 'libemploi_2010_2014',
#                                          mode='w', format='table', data_columns=True)


if __name__ == '__main__':

    arg_format_columns = [
        # ('c_netneh', range(2010, 2015), False),
        # ('c_cir', range(2010, 2015), False),
        # ('libemploi', range(2000, 2015), False),
        # # should contain _ otherwise libemploi which contains 'ib' would also selected
        ('ib_', range(1970, 2015), True),
        # ('qualite', range(1970, 2015), False),
        # ('statut', range(1970, 2015), False),
        # ('etat', range(1970, 2015), True),
        ]
    for args in arg_format_columns:
        format_columns(*args)

    format_generation()
