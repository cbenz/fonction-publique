# -*- coding:utf-8 -*-


from __future__ import division


import os
import pandas as pd


from fonction_publique.base import output_directory_path, clean_directory_path
from fonction_publique.merge_careers_and_legislation import fix_dtypes, get_grilles, get_libelles


def get_variables(variables = None, stop = None, decennie = None):
    """Recupere certaines variables de la table des carrières matchées avec grilles"""
    hdf5_file_path = os.path.join(output_directory_path, '{}_{}_carrieres.h5'.format(decennie, decennie + 9))
    return pd.read_hdf(hdf5_file_path, 'output', columns = variables, stop = stop)


def get_careers(variable = None, stop = None, decennie = None):
    """Recupere certaines variables de la table des carrières bruts"""

    careers_hdf_path = os.path.join(
        clean_directory_path,
        '{}_{}_carrieres.h5'.format(decennie, decennie + 9)
        )
    return pd.read_hdf(careers_hdf_path, variable, stop = stop)


def trimestres_par_generation():
    # distribution du nombres de trimestres par generation
    df = get_variables()
    fix_dtypes(df)

    tmp = df.groupby(['generation', 'ident'])['trimestre'].count().reset_index()
    tmp2 = tmp.groupby(['generation', 'trimestre']).count()



def analyse_grilles():
    # duree dans le rgade pour différente grilles
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

    max_mois = duree_carriere_by_grade.max_mois.sort_values(ascending = False) / 12
    max_mois.hist()

    tmp3 = duree_carriere_by_grade.reset_index()

    # Pour les 5 grilles les plus fréquentes
    for grade in ['TTH1', '3001', '2154', 'TAJ1', '3256', 'TTH3', 'TAJ2']:
        print get_libelles(code_grade_netneh = grade)
        print tmp3.query("code_grade == @grade")[['date_effet_grille', 'max_mois', 'min_mois', 'moy_mois']] / 12


def analyse_carriere():
    decennie = 1970
    carrieres = get_careers(variable = 'c_netneh', decennie = 1970)
    carrieres.tail(20)


    carrieres.groupby(['ident'])['c_netneh'].apply(
        lambda x: x != ''
        )

    tmp4 = carrieres.groupby(['ident'])['c_netneh'].unique()
    tmp4.tail()
    tmp5 = tmp4.reset_index()
    tmp5['sequence'] = tmp5.c_netneh.apply(lambda x: '-'.join(x))
    tmp6 = tmp5.groupby('sequence').size().sort_values(ascending = False)

    idents = carrieres.query("(c_netneh == '3001') & (annee == 2011)")['ident'].unique()
    len(idents)
    filtered = carrieres[carrieres.ident.isin(idents)]
    len(filtered)
    x = (filtered
        .groupby(['ident'])['c_netneh']
        .apply(lambda x: '-'.join(x))
        .value_counts()
        )

    toto1 = carrieres.groupby(['ident'])['c_netneh'].apply(lambda x: '-'.join(x))
    toto1.value_counts()

    clean_carrieres = (carrieres
        .fillna({'c_netneh': ''})
        .dropna(subset = ['c_netneh'])
        )

    tmp7 = clean_carrieres.groupby(['ident'])['c_netneh'].size()
    tmp7.value_counts()


    carrieres_libemploi = get_careers(variable = 'libemploi')
    carrieres_libemploi['libemploi'] = carrieres_libemploi.libemploi.replace(r'\s+', '', regex=True)
    carrieres_libemploi = carrieres_libemploi.query("libemploi != ''")
    carrieres_libemploi.head()

    tmp8 = carrieres_libemploi.groupby(['ident'])['libemploi'].size()
    tmp8.value_counts()

    tmp9 = carrieres_libemploi.groupby(['ident'])['libemploi'].unique().reset_index()
    tmp9.head()

    tmp9['sequence'] = tmp9.libemploi.apply(lambda x: '-'.join(x))
    tmp9.sequence.value_counts(ascending = False)
    tmp9.count()


    ib = get_careers(variable = 'ib')





