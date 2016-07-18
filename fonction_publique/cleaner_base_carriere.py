from __future__ import division
import os
import pandas as pd
import pylab as plt
import seaborn as sns
import time


# TODO: prepare data and export to hdf table

# path to stata data
data_path = "M:\CNRACL\Stata"



# Timer
def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap


# TODO move to the top
stata_file_path = os.path.join(data_path, 'c_g1950_g1959.dta')



def select_columns(string):  # e.g 'ident' 'qualite' 'statut' 'cir' '_netneh' 'libemploi' 'ib_' 'etat_'
#    colnames = read_only_store.select('data', 'index < 2').columns.to_series()
    """ selectionne les noms de colonnes correspondant à la variable (string) qui nous interesse """
    reader_for_colnames = pd.read_stata(stata_file_path, chunksize = 1)
    for chunk in reader_for_colnames:
        chunk_to_get_colnames = chunk
        break
    colnames = chunk_to_get_colnames.columns.to_series()
    colnames_subset = pd.Series(['ident'])
    colnames_to_keep = colnames.str.contains(string)
    colnames_kept = colnames[colnames_to_keep]
    colnames_subset = colnames_subset.append(colnames_kept)
    return colnames_subset.reset_index(drop = True)


@timing
def get_subset(string):
    """ selectionne le sous-dataframe pour une variable, appelee string ici"""
    reader = pd.read_stata(stata_file_path, chunksize = 50000)
    colnames = select_columns(string)
#    get_subset = read_only_store.select('data', 'columns = colnames')  # try full size
    get_subset = pd.DataFrame()
    for chunk in reader:
        subset = chunk[colnames]
        get_subset = get_subset.append(subset)
    return get_subset

#df_ib = get_subset('ib_')


@timing
def clean_subset(string, period, trimestre):
    """ nettoie chaque variable pour en faire un df propre """
    subset_result = pd.DataFrame()
    subset = get_subset(string)
    for annee in period:
        if trimestre:
            if string == 'ib_':
                for trimestre in range(1, 5):
                    subset_cleaned = subset[['ident', '{}{}_{}'.format(string, annee, trimestre)]].copy()
                    subset_cleaned.rename(
                        columns = {'{}{}_{}'.format(string, annee, trimestre): string},
                        inplace = True
                        )
                    subset_cleaned['trimestre'] = trimestre
                    subset_cleaned['annee'] = annee
                    subset_result = pd.concat([subset_result, subset_cleaned])
            else:
                subset_cleaned = subset[['ident', '{}_{}_{}'.format(string, annee, trimestre)]].copy()
                subset_cleaned.rename(
                    columns = {'{}_{}_{}'.format(string, annee, trimestre): string},
                    inplace = True
                    )
                subset_cleaned['trimestre'] = trimestre
                subset_cleaned['annee'] = annee
                subset_result = pd.concat([subset_result, subset_cleaned])
        else:
            subset_cleaned = subset[['ident', '{}_{}'.format(string, annee)]].copy()
            subset_cleaned.rename(columns = {'{}_{}'.format(string, annee): string}, inplace = True)
            subset_cleaned['annee'] = annee
            subset_result = pd.concat([subset_result, subset_cleaned])
    return subset_result


# TODO define a destination path
os.chdir('M:\CNRACL\Carriere-CNRACL/base_carriere_clean')



@timing
def format_columns(string, periode, trimestre):
    subset_to_format = clean_subset(string, periode, trimestre)
    subset_to_format['ident'] = subset_to_format['ident'].astype('int')
    if string in ['qualite', 'statut', 'etat_']:
        subset_to_format[string] = subset_to_format[string].astype('category')
    elif string in ['ident', '_netneh', 'cir', 'generation']:
        subset_to_format[string] = subset_to_format[string].astype('int')
    elif string in ['ib_']:
        subset_ib = subset_to_format['ib_'].fillna(-1)
        subset_ib = subset_ib.astype('int32')
        subset_to_format['ib_'] = subset_ib
    else:
        subset_to_format[string] = subset_to_format[string].astype('str')
    subset_to_format.to_hdf('base_carriere_2', '{}'.format(string), format = 'table', data_columns = True)
#    with pd.HDFStore('base_carriere_2',  mode='w') as store:
#        store.open()
#        store.put('{}'.format(string), subset_to_format, data_columns= subset_to_format.columns, format='table')
#        store.close()
    return 'df is cleaned'


def format_generation():
    generation = get_subset('generation')
    generation['ident'] = generation['ident'].astype('int')
    generation['generation'] = generation['generation'].astype('int32')
    generation.to_hdf('base_carriere_2', 'generation', format = 'table', data_columns = True)
    return 'generation was added to base_carriere'

#def gen_libemploi_2010_2014():
#    """ Cree une table libemploi_2010_2014 p'rovisoire pour comparer le nb de libelles grades sur la periode avec
#    les nb de codes grades sur la periodes. La table libemploi est en effet disponible pour 2000-2014.
#    """
#    df_libemploi = get_df('libemploi')
#    df_libemploi_subset = df_libemploi.to_hdf(hdf5_file_path, 'libemploi_2010_2014',
#                                          mode='w', format='table', data_columns=True)


if __name__ == '__main__':
    arg_format_columns = [
    ('c_netneh', range(2010, 2015), False),
    ('c_cir', range(2010, 2015), False),
    ('libemploi', range(2000, 2015), False),
    ('ib_', range(1970, 2015), True),
    ('qualite', range(1970, 2015), False),
    ('statut', range(1970, 2015), False),
    ('etat', range(1970, 2015), True)
    ]
