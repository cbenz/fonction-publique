# -*- coding:utf-8 -*-


from __future__ import division


import pandas as pd
from fonction_publique.base import timing


@timing
def clean_subset(variable, period, quarterly):
    """ nettoie chaque variable pour en faire un df propre """
    subset_result = pd.DataFrame()
    subset = pd.read_csv('/home/benjello/openfisca/fonction-publique/junk_ib.csv', index_col = 0)
    # Build a hierarchical index as in http://stackoverflow.com/questions/17819119/coverting-index-into-multiindex-hierachical-index-in-pandas

    for annee in period:
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
def new_clean_subset(variable, period, quarterly):
    """ nettoie chaque variable pour en faire un df propre """
    subset = pd.read_csv('/home/benjello/openfisca/fonction-publique/junk_ib.csv', index_col = 0)
    # Build a hierarchical index as in http://stackoverflow.com/questions/17819119/coverting-index-into-multiindex-hierachical-index-in-pandas

    def process_index(k):
        return tuple(k.split("_"))

    assert not subset.ident.duplicated().any()
    subset = subset.set_index('ident')

    if quarterly:
        subset.columns = pd.MultiIndex.from_tuples(
            [process_index(k) for k in subset.columns],
            names = ['index', 'annee', 'trimestre']
            )
        stacked = subset.stack('annee').stack('trimestre').reset_index()
        stacked['trimestre'] = pd.to_numeric(stacked.trimestre)

    else:
        subset.columns = pd.MultiIndex.from_tuples(
            [process_index(k) for k in subset.columns],
            names = ['index', 'annee']
            )
        stacked = subset.stack('annee').reset_index()

    stacked['annee'] = pd.to_numeric(stacked.annee)
    return stacked


if __name__ == '__main__':

    arg_format_columns = [
        ('ib_', range(1970, 2015), True),
        ]
    for args in arg_format_columns:
        x = clean_subset(*args)
        y = new_clean_subset(*args)
        print x.dtypes
        print y.dtypes
        print x[['ident', 'annee', 'trimestre', 'ib_']].sort_values(by = ['ident', 'annee', 'trimestre']).head()
        print y[['ident', 'annee', 'trimestre', 'ib']].sort_values(by = ['ident', 'annee', 'trimestre']).head()
        print x.equals(y)
        print len(y) / len(x)
