# -*- coding: utf-8 -*-


## Test sur corps des techniciens de la FPT

# Filters: individuals at least one time in the corps
from __future__ import division

import logging
import inspect
import os
import sys
import pkg_resources
import pandas as pd
import numpy as np



from fonction_publique.base import raw_directory_path, get_careers, parser
from fonction_publique.merge_careers_and_legislation import get_grilles
from slugify import slugify

libelles_emploi_directory = parser.get('correspondances', 'libelles_emploi_directory')
save_path = 'M:/CNRACL/output'


def select_grilles(corps):
    path_grilles = os.path.join(
    pkg_resources.get_distribution('fonction_publique').location,
    'fonction_publique',
    'assets',
    'grilles_fonction_publique',
    )
    grilles = pd.read_hdf(os.path.join(path_grilles,"grilles_old.h5"))
    if corps == 'AT':
        libNEG_corps = ['ADJOINT TECHNIQUE DE 2EME CLASSE', 'ADJOINT TECHNIQUE DE 1ERE CLASSE',
                        'ADJOINT TECHNIQUE PRINCIPAL DE 2EME CLASSE', 'ADJOINT TECHNIQUE PRINCIPAL DE 1ERE CLASSE']
    if corps == 'AA':
        libNEG_corps = ['ADJOINT ADMINISTRATIF DE 2EME CLASSE', 'ADJOINT ADMINISTRATIF DE 1ERE CLASSE',
                    'ADJOINT ADMINISTRATIF PRINCIPAL DE 2EME CLASSE', 'ADJOINT ADMINISTRATIF PRINCIPAL DE 1ERE CLASSE']
    if corps == 'ES':
        libNEG_corps = ['AIDE SOIGNANT CL NORMALE (E04)', 'AIDE SOIGNANT CL SUPERIEURE (E05)',
                        'AIDE SOIGNANT CL EXCEPT (E06)']
    subset_grilles = grilles[grilles.libelle_grade_NEG.isin(libNEG_corps)]
    return (subset_grilles)

def select_ident(dataset):
    variable =  'c_neg'
    c_neg =  get_careers(variable = variable, data_path = dataset)
    subset_by_corps = {}
    for corps in ['AT', 'AA', 'ES']:
        grilles = select_grilles(corps = corps)
        list_code = list(set(grilles.code_grade_NEG.astype(str)))
        list_code = ['0' + s for s in list_code]
        subset_ident = list(set(c_neg.ident[c_neg.c_neg.isin(list_code)]))
        subset_by_corps[corps] = subset_ident

    return subset_by_corps

def cleaning_data(dataset, subset_by_corps, corps):
    # Filter
    subset_ident = subset_by_corps[corps]
    # Load data by type
    where = "ident in {}".format(subset_ident)
    permanent_variables = ['generation', 'sexe', 'an_aff']
    generation =  get_careers(variable = permanent_variables[0], data_path = dataset, where = where)
    sexe =  get_careers(variable = permanent_variables[1], data_path = dataset, where = where)
    an_aff =  get_careers(variable = permanent_variables[2], data_path = dataset, where = where)
    data_i = generation.merge(sexe, how = "left", on = ['ident']).merge(an_aff, how = "left", on = ['ident']).sort_values(['ident'])
    del an_aff, generation, sexe

    where = "(ident in {}) & (annee > 2004)".format(subset_ident)
    quaterly_variables =  ['ib', 'echelon']
    ib  =  get_careers(variable = quaterly_variables[0], data_path = dataset, where = where)
    ib  =  ib.pivot_table(index= ['ident', 'annee'], columns='trimestre', values='ib').reset_index()
    ib.columns = ['ident', 'annee', 'ib1', 'ib2', 'ib3', 'ib4']
    ech =  get_careers(variable = quaterly_variables[1], data_path = dataset, where = where)
    ech.echelon =  pd.to_numeric(ech.echelon, errors='coerce')
    ech  =  ech.pivot_table(index= ['ident', 'annee'], columns='trimestre', values='echelon').reset_index()
    ech.columns = ['ident', 'annee', 'echelon1', 'echelon2', 'echelon3', 'echelon4']

    where = "(ident in {}) & (annee > 2004)".format(subset_ident)
    yearly_variables =  ['c_neg', 'libemploi', 'statut']
    c_neg =  get_careers(variable = yearly_variables[0], data_path = dataset, where = where)
    libemploi =  get_careers(variable = yearly_variables[1], data_path = dataset, where = where)
    statut =  get_careers(variable = yearly_variables[2], data_path = dataset, where = where)

    # Merge time varying variables
    data = (libemploi
                .merge(c_neg, how = "left", on = ['ident', 'annee'])
                .merge(statut, how = "left", on = ['ident', 'annee'])
                .merge(ib, how = "left", on = ['ident', 'annee'])
                .merge(ech, how = "left", on = ['ident', 'annee'])
                .sort_values(['ident', 'annee'])
            )
    # Merge two data
    data = data.merge(data_i, how = "left", on = ['ident'])
    # Drop duplicates
    a = len(set(data.ident))
    data = data.drop_duplicates(subset = ['ident', 'annee'], keep = False)
    b = len(set(data.ident))
    diff = a - b
    #print("{}: {} individus dupliqués et supprimés".format(dataset, diff))

    return data


def main():
    datasets = ['1980_1999_carrieres.h5',
                '1976_1979_carrieres.h5',
                '1970_1975_carrieres.h5',
                '1960_1965_carrieres.h5',
                '1966_1969_carrieres.h5',
                ]
    for dataset in datasets:
        print("Processing data {}".format(dataset))
        # List of ident
        subset_by_corps = select_ident(dataset)
        # Load and clean data by corps
   #     data_AA = cleaning_data(dataset, subset_by_corps, corps = 'AA')
   #     data_AT = cleaning_data(dataset, subset_by_corps, corps = 'AT')
        data_ES = cleaning_data(dataset, subset_by_corps, corps = 'ES')

        if dataset == datasets[0]:
   #         data_merge_AA = data_AA
   #         data_merge_AT = data_AT
            data_merge_ES = data_ES
        else:
   #         data_merge_AA = data_merge_AA.append(data_AA)
   #         data_merge_AT = data_merge_AA.append(data_AT)
            data_merge_ES = data_merge_ES.append(data_ES)

#    path = os.path.join(save_path, "corpsAA.csv")
#    data_merge_AA.to_csv(path)
#    path = os.path.join(save_path, "corpsAT.csv")
#    data_merge_AT.to_csv(path)
    path = os.path.join(save_path, "corpsES.csv")
    data_merge_ES.to_csv(path)

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    main()
