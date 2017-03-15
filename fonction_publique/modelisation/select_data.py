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


def cleaning_data(generation, sexe, an_aff, libemploi, statut, c_neg, echelon, ib, corps):
    # Grilles
    grilles = select_grilles(corps)
    # Indiv avec un lib dans le corps
    list_code = list(set(grilles.code_grade_NEG.astype(str)))
    list_code = ['0' + s for s in list_code]
    subset_ident = list(set(c_neg.ident[c_neg.c_neg.isin(list_code)]))
    # Merge individual variables
    generation_subset = generation.loc[generation.ident.isin(subset_ident)].sort_values(['ident'])
    an_aff_subset = an_aff.loc[an_aff.ident.isin(subset_ident)].sort_values(['ident'])
    sexe_subset = sexe.loc[sexe.ident.isin(subset_ident)].sort_values(['ident'])
    data_i = (generation_subset
              .merge(sexe_subset, how = "left", on = ['ident'])
              .merge(an_aff_subset, how = "left", on = ['ident']))
    # Merge time varying variables
    c_neg_subset = c_neg.loc[c_neg.ident.isin(subset_ident)].sort_values(['ident', 'annee'])
    statut_subset = statut.loc[statut.ident.isin(subset_ident)].sort_values(['ident', 'annee'])
    libemploi_subset = libemploi.loc[libemploi.ident.isin(subset_ident)].sort_values(['ident', 'annee'])
    ib_subset = ib.loc[ib.ident.isin(subset_ident)].sort_values(['ident', 'annee'])
    echelon_subset = echelon.loc[echelon.ident.isin(subset_ident)].sort_values(['ident', 'annee'])

    ib_subset1 = ib_subset.loc[(ib_subset.trimestre == 1)][['ident', 'annee', 'ib']].rename(columns={'ib':'ib1'})
    ib_subset2 = ib_subset.loc[(ib_subset.trimestre == 2)][['ident', 'annee', 'ib']].rename(columns={'ib':'ib2'})
    ib_subset3 = ib_subset.loc[(ib_subset.trimestre == 3)][['ident', 'annee', 'ib']].rename(columns={'ib':'ib3'})
    ib_subset4 = ib_subset.loc[(ib_subset.trimestre == 4)][['ident', 'annee', 'ib']].rename(columns={'ib':'ib4'})
    echelon_subset1 = echelon_subset.loc[(echelon_subset.trimestre == 1)][['ident', 'annee', 'echelon']].rename(columns={'echelon':'echelon1'})
    echelon_subset2 = echelon_subset.loc[(echelon_subset.trimestre == 2)][['ident', 'annee', 'echelon']].rename(columns={'echelon':'echelon2'})
    echelon_subset3 = echelon_subset.loc[(echelon_subset.trimestre == 3)][['ident', 'annee', 'echelon']].rename(columns={'echelon':'echelon3'})
    echelon_subset4 = echelon_subset.loc[(echelon_subset.trimestre == 4)][['ident', 'annee', 'echelon']].rename(columns={'echelon':'echelon4'})

    data = (libemploi_subset
                .merge(c_neg_subset, how = "left", on = ['ident', 'annee'])
                .merge(statut_subset, how = "left", on = ['ident', 'annee'])
                .merge(ib_subset1, how = "left", on = ['ident', 'annee'])
                .merge(ib_subset2, how = "left", on = ['ident', 'annee'])
                .merge(ib_subset3, how = "left", on = ['ident', 'annee'])
                .merge(ib_subset4, how = "left", on = ['ident', 'annee'])
                .merge(echelon_subset1, how = "left", on = ['ident', 'annee'])
                .merge(echelon_subset2, how = "left", on = ['ident', 'annee'])
                .merge(echelon_subset3, how = "left", on = ['ident', 'annee'])
                .merge(echelon_subset4, how = "left", on = ['ident', 'annee'])
                .sort_values(['ident', 'annee'])
            )
    # Merge two data
    data = data.merge(data_i, how = "left", on = ['ident'])
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
    datasets = ['1980_1999_carrieres.h5',]
#                 '1976_1979_carrieres.h5',
#                 '1970_1975_carrieres.h5',
#                 '1960_1965_carrieres.h5',
#                 '1966_1969_carrieres.h5',
#                 ]
#    for dataset in datasets:
    dataset = '1980_1999_carrieres.h5'
    print("Processing data {}".format(dataset))
       # Fix variables
    variable =  'c_neg'  #'statut', 'libemploi',
    c_neg =  get_careers(variable = variable, data_path = dataset)

    corps = 'AA'
    grilles = select_grilles(corps = corps)
    list_code = list(set(grilles.code_grade_NEG.astype(str)))
    list_code = ['0' + s for s in list_code]
    subset_ident = list(set(c_neg.ident[c_neg.c_neg.isin(list_code)]))
    del c_neg
    import gc
    gc.collect()
    print(subset_ident[:10])
    permanent_variables = ['generation', 'sexe', 'an_aff']
    where = "ident in {}".format(subset_ident)  # "[3801063, 2097128, 2097131, 3801072, 2097146, 2097150]"
    permanent =  get_careers(variables = permanent_variables, data_path = dataset, where = where)
    print permanent
    BOUM

    permanent_variables = ['generation', 'sexe', 'an_aff']
    permanent =  get_careers(variables = permanent_variables, data_path = dataset)


    quaterly_variables =  ['ib', 'echelon']






    an_aff =  get_careers(variable = 'an_aff', data_path = dataset)
    sexe =  get_careers(variable = 'sexe', data_path = dataset)
    # Carrière
    libemploi = load_career('libemploi', dataset)
    c_neg = load_career('c_neg', dataset)
    statut = load_career('statut', dataset)
    ib = load_career('ib', dataset)
    echelon = load_career('echelon', dataset).sort_values(['ident', 'annee','trimestre'])

    data_AA = cleaning_data(generation, sexe, an_aff, libemploi, statut, c_neg, echelon, ib, 'AA')
    data_AT = cleaning_data(generation, sexe, an_aff, libemploi, statut, c_neg, echelon, ib, 'AT')
    data_ES = cleaning_data(generation, sexe, an_aff, libemploi, statut, c_neg, echelon, ib, 'ES')

    if data == list_data[0]:
        data_merge_AA = data_AA
        data_merge_AT = data_AT
        data_merge_ES = data_ES
    else:
        data_merge_AA = data_merge_AA.append(data_AA)
        data_merge_AT = data_merge_AA.append(data_AT)
        data_merge_ES = data_merge_AA.append(data_ES)

    path = os.path.join(save_path, "corpsAA.csv")
    data_merge_AA.to_csv(path)
    path = os.path.join(save_path, "corpsAT.csv")
    data_merge_AT.to_csv(path)
    path = os.path.join(save_path, "corpsES.csv")
    data_merge_ES.to_csv(path)

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    main()
