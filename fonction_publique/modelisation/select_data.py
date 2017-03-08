# -*- coding: utf-8 -*-


## Test sur corps des techniciens de la FPT

# Filters: individuals at least one time in the corps

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


def load_career(var, data):
    career = get_careers(variable = var, data_path = data, debug = False)
    career = career.loc[career.annee>1999].copy()
    return career

def select_ident(libemploi):
    libemploi['libemploi_slugified'] = libemploi.libemploi.apply(slugify, separator = "_")
    libemploi_corps = ['adjoint_technique_de_2eme_classe', 'adjoint_technique_de_1ere_classe',
                       'adjoint_technique_principal_de_2eme_classe', 'adjoint_technique_principal_de_1ere_classe']
    subset_libemploi = libemploi[libemploi.libemploi_slugified.isin(libemploi_corps)]
    subset_ident = subset_libemploi.ident.unique()
    return subset_ident


def select_grilles():
    path_grilles = os.path.join(
    pkg_resources.get_distribution('fonction_publique').location,
    'fonction_publique',
    'assets',
    'grilles_fonction_publique',
    )
    grilles = pd.read_hdf(os.path.join(path_grilles,"grilles_old.h5"))
    libNEG_corps = ['ADJOINT TECHNIQUE DE 2EME CLASSE', 'ADJOINT TECHNIQUE DE 1ERE CLASSE',
                    'ADJOINT TECHNIQUE PRINCIPAL DE 2EME CLASSE', 'ADJOINT TECHNIQUE PRINCIPAL DE 1ERE CLASSE']
    subset_grilles = grilles[grilles.libelle_grade_NEG.isin(libNEG_corps)]
    return (subset_grilles)


def cleaning_data(dataset):
    # Fix variables
    #generation =  get_careers(variable = 'generation', data_path = dataset)
    # Carrière
    libemploi = load_career('libemploi', dataset)
    c_neg = load_career('c_neg', dataset)
    statut = load_career('statut', dataset)
    ib = load_career('ib', dataset)
    ib_subset = ib.loc[(ib.trimestre == 1)][['ident', 'annee', 'ib']]
    echelon = load_career('echelon', dataset)
    echelon_subset = echelon.loc[(echelon.trimestre == 1)][['ident', 'annee', 'echelon']]
    # Grilles
    grilles = select_grilles()
    # Indiv avec un lib dans le corps
    list_code = list(set(grilles.code_grade_NEG.astype(str)))
    list_code = ['0' + s for s in list_code]
    subset_ident = list(set(c_neg.ident[c_neg.c_neg.isin(list_code)]))
    # Merge lib + neg + ib
    c_neg_subset = c_neg.loc[c_neg.ident.isin(subset_ident)].sort_values(['ident', 'annee'])
    statut_subset = statut.loc[statut.ident.isin(subset_ident)].sort_values(['ident', 'annee'])
    libemploi_subset = libemploi.loc[libemploi.ident.isin(subset_ident)].sort_values(['ident', 'annee'])
    ib_subset = ib_subset.loc[ib_subset.ident.isin(subset_ident)].sort_values(['ident', 'annee'])
    echelon_subset = echelon_subset.loc[echelon_subset.ident.isin(subset_ident)].sort_values(['ident', 'annee'])
    # Merge
    data = (libemploi_subset
                .merge(c_neg_subset, how = "left", on = ['ident', 'annee'])
                .merge(statut_subset, how = "left", on = ['ident', 'annee'])
                .merge(ib_subset, how = "left", on = ['ident', 'annee'])
                .merge(echelon_subset, how = "left", on = ['ident', 'annee'])
                .sort_values(['ident', 'annee'])
            )
    # Drop duplicates
    a = len(set(data.ident))
    data = data.drop_duplicates(subset = ['ident', 'annee'], keep = False)
    b = len(set(data.ident))
    diff = a - b
    print("{}: {} individus dupliqués et supprimés".format(dataset, diff))

    # Final selection on year and missing lib
    clean_data = data.loc[data.annee > 2004].copy()

    return clean_data


def main():
    list_data = ['1960_1965_carrieres.h5','1966_1969_carrieres.h5',
                 '1970_1975_carrieres.h5','1976_1979_carrieres.h5',
                 '1980_1999_carrieres.h5']
    for data in list_data:
        print("Processing data {}".format(data))
        clean_data = cleaning_data(data)
        if data == list_data[0]:
            data_merge = clean_data
        else:
            data_merge = data_merge.append(clean_data)

    path = os.path.join(save_path, "corpsAT.csv")
    data_merge.to_csv(path)

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    main()
