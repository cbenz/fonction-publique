# -*- coding: utf-8 -*-
from __future__ import division


import logging
import os
import pandas as pd

import pkg_resources

from fonction_publique.base import get_careers, grilles, output_directory_path


log = logging.getLogger(__name__)



def select_grilles(corps):
    path_grilles = os.path.join(
        pkg_resources.get_distribution('fonction_publique').location,
        'fonction_publique',
        'assets',
        'grilles_fonction_publique',
        )
    grilles = pd.read_hdf(os.path.join(path_grilles, "grilles_old.h5"))
    if corps == 'AT':
        libNEG_corps = ['ADJOINT TECHNIQUE DE 2EME CLASSE',
                        'ADJOINT TECHNIQUE DE 1ERE CLASSE',
                        'ADJOINT TECHNIQUE PRINCIPAL DE 2EME CLASSE',
                        'ADJOINT TECHNIQUE PRINCIPAL DE 1ERE CLASSE'
                        ]
    elif corps == 'AA':
        libNEG_corps = ['ADJOINT ADMINISTRATIF DE 2EME CLASSE',
                        'ADJOINT ADMINISTRATIF DE 1ERE CLASSE',
                        'ADJOINT ADMINISTRATIF PRINCIPAL DE 2EME CLASSE',
                        'ADJOINT ADMINISTRATIF PRINCIPAL DE 1ERE CLASSE'
                        ]
    elif corps == 'AS':
        libNEG_corps = ['AIDE SOIGNANT CL NORMALE (E04)',
                        'AIDE SOIGNANT CL SUPERIEURE (E05)',
                        'AIDE SOIGNANT CL EXCEPT (E06)'
                        ]
    else:
        raise ValueError("NEG for the corps are not specified in the select_grilles function")
        
    subset_grilles = grilles[grilles.libelle_grade_NEG.isin(libNEG_corps)]
    return (subset_grilles)


def select_ident(corps, dataset, grilles, selection_variable):
    log.info('Entering corps {}'.format(corps))
    if (selection_variable == 'c_neg'):
        assert corps in['AT', 'AA', 'AS'], "C_NEG for the corps are not specificied in select_grilles"
        c_neg = get_careers(variable = selection_variable, data_path = dataset)
        subset_by_corps = {}
        for corps in ['AT', 'AA', 'AS']:
            grilles = select_grilles(corps = corps)
            list_code = list(set(grilles.code_grade_NEG.astype(str)))
            list_code = ['0' + s for s in list_code]
            subset_ident = list(set(c_neg.ident[c_neg.c_neg.isin(list_code)]))
            subset_by_corps[corps] = subset_ident
    if (selection_variable == 'c_cir'):        
        data_grade = get_careers(variable = selection_variable, data_path = dataset)
        subset_by_corps = dict()
        assert 'corps_NETNEH' in grilles.columns, 'corps_NETNEH is not available in grilles columns: \n {}'.format(
            grilles.columns,
            )
        assert corps in grilles.corps_NETNEH.unique().tolist(), "NETNEH for the corps are not included in grilles.h5"
        grilles = grilles.query('corps_NETNEH in @corps').copy()
        grades_keep = grilles.code_grade_NETNEH.unique().tolist()
        for grade in grades_keep:
            if grade in ['TTH1', 'TTH2', 'TTH3', 'TTH4']:
                grades_keep.append('S' + grade[-3:])  # Include stagiaires
        subset_ident = list(set(data_grade.ident[data_grade.c_cir.isin(grades_keep)]))
        subset_by_corps[corps] = subset_ident        
    return subset_by_corps



def select_variables(corps, dataset, first_year, grilles, subset_by_corps):
    subset_ident = subset_by_corps[corps]
    where = "ident in {}".format(subset_ident)
    permanent_variables = ['generation', 'sexe', 'an_aff']
    generation = get_careers(variable = permanent_variables[0], data_path = dataset, where = where)
    sexe = get_careers(variable = permanent_variables[1], data_path = dataset, where = where)
    an_aff = get_careers(variable = permanent_variables[2], data_path = dataset, where = where)
    data_i = generation.merge(
        sexe, how = "left", on = ['ident']
        ).merge(an_aff, how = "left", on = ['ident']).sort_values(['ident'])
    del an_aff, generation, sexe
    where = "(ident in {}) & (annee >= {})".format(subset_ident, first_year)
    quaterly_variables = ['ib', 'echelon', 'etat']
    ib = get_careers(variable = quaterly_variables[0], data_path = dataset, where = where)
    ib = ib.pivot_table(index= ['ident', 'annee'], columns='trimestre', values='ib').reset_index()
    ib.columns = ['ident', 'annee', 'ib1', 'ib2', 'ib3', 'ib4']
    ech = get_careers(variable = quaterly_variables[1], data_path = dataset, where = where)
    ech.echelon = pd.to_numeric(ech.echelon, errors='coerce')
    ech = ech.pivot_table(index= ['ident', 'annee'], columns='trimestre', values='echelon').reset_index()
    ech.columns = ['ident', 'annee', 'echelon1', 'echelon2', 'echelon3', 'echelon4']
    etats = get_careers(variable = quaterly_variables[2], data_path = dataset, where = where)
    etats.etat = pd.to_numeric(etats.etat, errors='coerce')
    etats = etats.pivot_table(index= ['ident', 'annee'], columns='trimestre', values='etat').reset_index()
    etats.columns = ['ident', 'annee', 'etat1', 'etat2', 'etat3', 'etat4']
    where = "(ident in {}) & (annee >= {})".format(subset_ident, first_year)
    yearly_variables = ['c_cir', 'libemploi', 'statut']
    c_cir = get_careers(variable = yearly_variables[0], data_path = dataset, where = where)
    libemploi = get_careers(variable = yearly_variables[1], data_path = dataset, where = where)
    statut = get_careers(variable = yearly_variables[2], data_path = dataset, where = where)
    data = (libemploi
        .merge(c_cir, how = "left", on = ['ident', 'annee'])
        .merge(statut, how = "left", on = ['ident', 'annee'])
        .merge(ib, how = "left", on = ['ident', 'annee'])
        .merge(ech, how = "left", on = ['ident', 'annee'])
        .merge(etats, how = "left", on = ['ident', 'annee'])
        .sort_values(['ident', 'annee'])
        )
    data = data.merge(data_i, how = "left", on = ['ident'])
    a = len(set(data.ident))
    data = data.drop_duplicates(subset = ['ident', 'annee'], keep = False)
    b = len(set(data.ident))
    diff = a - b
    log.info("{}: {} individus dupliqués et supprimés".format(dataset, diff))
    return data


def main(datasets = None, first_year = None, grilles = grilles, list_corps = None, save_path = None, selection_variable = None):
    data_merge_corps = {}
    for dataset in datasets:
        log.info("Processing data {}".format(dataset))
        for corps in list_corps:
            log.info("Processing corps {}".format(corps))
            subset_by_corps = select_ident(corps, dataset, grilles, selection_variable)
            log.info("Nb ind: {}".format(len(subset_by_corps[corps])))
            BAMMM
            
            data_cleaned = select_variables(
                corps,
                dataset,
                first_year,
                grilles,
                subset_by_corps,
                )
            if dataset == datasets[0]:
                data_merge_corps["data_corps_{}".format(corps)] = data_cleaned
            else:
                data_merge = data_merge_corps["data_corps_{}".format(corps)].append(data_cleaned)
                data_merge_corps["data_corps_{}".format(corps)] = data_merge
    for corps in list_corps:
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        path = os.path.join(
            save_path,
            "corps{}_{}.csv".format(corps, first_year)
            )
        data_merge_corps["data_corps_{}".format(corps)].to_csv(path)

        log.info("Saving {} data for year {} in {}".format(corps, first_year, path))

    return


if __name__ == '__main__':
    main(
        datasets = [
            '1960_1965_carrieres.h5',
            '1966_1969_carrieres.h5',
            '1970_1975_carrieres.h5',
            '1976_1979_carrieres.h5',
            '1980_1999_carrieres.h5',
            ],
        first_year = 2000,
        save_path = os.path.join(output_directory_path, 'select_data'),
        list_corps = ['AT'],
        selection_variable = "c_neg",
    #    list_corps = ['adjoints techniques territoriaux'],
    #    selection_variable = "c_cir",
        )
