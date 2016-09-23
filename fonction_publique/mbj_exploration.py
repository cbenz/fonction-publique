# -*- coding:utf-8 -*-


from __future__ import division


from collections import Counter
import numpy as np
import os
import pandas as pd
import pylab as plt
import seaborn as sns


from fonction_publique.base import cnracl_path, output_directory_path, clean_directory_path, law_hdf_path
from fonction_publique.merge_careers_and_legislation import fix_dtypes

hdf5_file_path = os.path.join(output_directory_path, '1950_1959.hdf5')


store = pd.HDFStore(hdf5_file_path)


def get_variables(variables = None, stop = None):
    """Recupere une table du store en fonction du nom de la variable"""
    return pd.read_hdf(hdf5_file_path, 'output', columns = variables, stop = stop)


def get_grilles():
    return pd.read_hdf(law_hdf_path)


df = get_variables()
fix_dtypes(df)

df.dtypes


df.groupby('ident')['code_grade'].unique()


tmp = df.groupby(['generation', 'ident'])['trimestre'].count().reset_index()

tmp2 = tmp.groupby(['generation', 'trimestre']).count()


grilles = get_grilles()
grilles.columns

echelon_max = grilles.groupby(['code_grade', 'date_effet_grille'])['echelon'].max()

aggregations = {
    'max_mois': 'sum',
    'min_mois': 'sum',
    'moy_mois': 'sum',
    }


duree_carriere_by_grade = grilles.groupby(['code_grade', 'date_effet_grille']).agg(
    aggregations)


max_mois = (duree_carriere_by_grade.max_mois.sort_values(ascending = False) / 12
max_mois.hist()



