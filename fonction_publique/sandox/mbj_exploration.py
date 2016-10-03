# -*- coding:utf-8 -*-


from __future__ import division


import pandas as pd


from fonction_publique.base import get_careers, get_variables
from fonction_publique.bordeaux.utils import get_transitions_dataframe, clean_empty_netneh, get_destinations_dataframe

from fonction_publique.merge_careers_and_legislation import fix_dtypes, get_grilles, get_libelles




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


if __name__ == '__main__':
    decennie = 1970
    carrieres = get_careers(variable = 'c_netneh', decennie = decennie).sort_values(['ident', 'annee'])
    carrieres = clean_empty_netneh(carrieres.query('annee > 2010'))


    get_destinations_dataframe(carrieres=carrieres, initial_grades = ['TAJ2', 'TTH2'])


    codes = set(destinations.initial.unique()).union(set(destinations.destination.unique()))
    for code in codes:
        print code , get_libelles(code_grade_netneh = code)[ 'libelle_grade_NEG'].squeeze()

    destinations.merge(total)
    extended.loc[initial_grades].nlargest(n_destinations)

    result = dict(root = initial_grades)

    for child in result.itervalues():
        initial_grade = child
        value_by_destination_grades = extended.loc[initial_grade].nlargest(n_destinations).to_dict()


    initial_grade = [1]

    def run(result, iteration = 0, stop = 3):
        if iteration == stop:
            print iteration
            return

        for parent, children in result.iteritems():
            destination_by_child = dict()
            for child in children:
                initial_grade = child
                print initial_grade
                value_by_destination_grades = (extended.loc[initial_grade].nlargest(n_destinations)).to_dict()
                destination_by_child[child] = value_by_destination_grades.keys()
            children = destination_by_child


            run(iter_result, iteration = iteration + 1, stop = stop)

    run(result)

    def get_nlargest_destination(initial_grades):
        destinations_by_intial_grades = (extended.loc[initial_grades]
            .T
            )
        destinations_by_intial_grades = destinations_by_intial_grades.stack()
        destinations_by_intial_grades.to_dict()

    initial_grades

    new_initial_grades = set(initial_grades + destination_grades)

    destinations_by_new_intial_grades = extended.loc[new_initial_grades].copy().T.apply(lambda x: x.nlargest(n_destinations)).T
    destination_grades = destinations_by_new_intial_grades.columns.tolist()

    all_grades = set(list(new_initial_grades) + destination_grades)

    shrinked = extended.loc[all_grades, all_grades]
    shrinked = shrinked.reindex_axis(shrinked.index, axis = 1)
    # shrinked = shrinked.rename(columns = dict(zip(shrinked.columns, 'y' + shrinked.columns.str[1:])))

    nodes = pd.DataFrame()
    nodes['ID'] = list(all_grades)
    nodes.set_index('ID', inplace = True)
    nodes['x'] = 3
    nodes.loc[new_initial_grades, 'x'] = 2
    nodes.loc[initial_grades, 'x'] = 1
    nodes['ID'] = nodes.index
    nodes

    proto_edges = shrinked.copy()
    proto_edges['N1'] = shrinked.index
    edges = pd.melt(proto_edges, id_vars = 'N1', var_name = 'N2', value_name = 'Value').reset_index(drop = True)
    new_edges = edges.loc[
        edges.N1.isin(new_initial_grades) &
        edges.N2.isin(destination_grades)
        ].copy()

    shrinked.to_csv('transition_matrix.csv')
    nodes.to_csv('nodes.csv')

    # TODO rajouter les autres

    get_libelles(code_grade_netneh = '2753')