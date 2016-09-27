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

def build_transitions_pct_by_echantillon(decennie = 1970):
    carrieres = get_careers(variable = 'c_netneh', decennie = decennie).sort_values(['ident', 'annee'])
    carrieres['c_netneh'] = carrieres.c_netneh.replace(r'\s+', '', regex = True)

    def get_transitions(carrieres, normalize = True):
        transitions = pd.DataFrame()
        selection = carrieres.c_netneh.shift().notnull() & (carrieres.ident == carrieres.shift().ident)
        transitions['ident'] = carrieres.ident[selection]
        transitions['transition'] = (carrieres.c_netneh != carrieres.c_netneh.shift())[selection]
        return transitions.groupby('ident').sum().astype(int).squeeze().value_counts(normalize = normalize)

    def clean_empty_netneh(df):
        df = df.copy()
        df['dummy'] = df.c_netneh == ''
        dummy_by_ident = (df.groupby('ident')['dummy'].sum() == 0).reset_index()
        idents = dummy_by_ident.query('dummy').ident.unique()
        return df[df.ident.isin(idents)].copy()

    return pd.concat(dict(
        annees_2010_2014 = get_transitions(carrieres),
        annees_2011_2014 = get_transitions(carrieres[carrieres.annee != 2010]),
        annees_2010_2014_purgees = get_transitions(clean_empty_netneh(carrieres)),  # 110 transitions,
        annees_2011_2014_purgees = get_transitions(clean_empty_netneh(carrieres.query('annee != 2010'))),  # 390701
        )).reset_index().rename(
            columns = {
                'level_0': 'echantillon',
                'level_1': 'transitions',
                'transition': 'population',
                }
            ).sort_values(['echantillon', 'transitions'])


if __name__ == '__main__':

    transitions_pct_by_echantillon = build_transitions_pct_by_echantillon(decennie = 1970)

    transitions_pct_by_grade_initial = build_transitions_pct_by_grade_initial(decennie = 1970)


def build_transitions_pct_by_grade_initial(decennie = 1970):
    def get_transitions_grade_init(carrieres):
        df = pd.DataFrame()
        selection = carrieres.c_netneh.shift().notnull() & (carrieres.ident == carrieres.shift().ident)
        df['ident'] = carrieres.ident[selection]
        premiere_annee = carrieres.annee.min()  # analysis:ignore

        premier_grade = carrieres.query('annee == @premiere_annee')[['ident', 'c_netneh']]
        df['transition'] = (carrieres.c_netneh != carrieres.c_netneh.shift())[selection]
        transitions = (df
            .merge(premier_grade, on = 'ident', how = 'left')
            .groupby(['ident', 'c_netneh'])['transition']
            .sum()
            .astype(int)
            .reset_index()
            )
        result = pd.DataFrame()
        result['population'] = (transitions
            .groupby('c_netneh')['transition']
            .value_counts()
            .sort_values(ascending = False)
            .cumsum()
            )
        result['cdf'] = result.population / result.population.max()
        return result

    return pd.concat(dict(
        annees_2010_2014 = get_transitions_grade_init(carrieres),
        annees_2011_2014 = get_transitions_grade_init(carrieres[carrieres.annee != 2010]),
        annees_2010_2014_purgees = get_transitions_grade_init(clean_empty_netneh(carrieres)),
        annees_2011_2014_purgees = get_transitions_grade_init(clean_empty_netneh(carrieres.query('annee != 2010'))),
        ))
