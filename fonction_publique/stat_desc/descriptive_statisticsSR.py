# -*- coding: utf-8 -*-
"""
Descriptive statistics for CNRACL
I. Point of missing values (MV): frequency, type (non work vs. MV) for year 2014
II. Comparaison grade NEG and grade NETNEH (analysis of the correspondance table)
    II.1 Analysis of the correspondance table NETNEH/NEG
    II.2 From NETNEH in the data to NEG
"""




"""
TODO: list of NETNEH code when Libelles slugified in:
INFIRMIER DE DE CLASSE SUPERIEURE
OUVRIER PROFESSIONNEL QUALIFIE E4
AIDE SOIGNANT DE CLASSE EXCEPTIONNELLE E6
ADJOINT ADMINISTRATIF HOSPITALIER DE 2EME CLASSE
"""


# 0. Imports

from __future__ import division

import logging
import os
import pandas as pd
import numpy as np
import sys


from fonction_publique.matching_grade.grade_matching import get_correspondance_data_frame, validate_correspondance
from fonction_publique.merge_careers_and_legislation import get_grilles
from fonction_publique.base import clean_directory_path, raw_directory_path, get_careers, parser

log = logging.getLogger(__name__)

debug = False

def load_libelles(decennie = 1980, debug = False, year = 2014):
    libemploi = get_careers(variable = 'libemploi', decennie = decennie, debug = debug)
    libemploi['libemploi_slugified'] = libemploi.libemploi.apply(slugify, separator = "_")
    statut = get_careers(variable = 'statut', decennie = decennie, debug = debug)
    libemploi = (libemploi
        .merge(
            statut,
            how = 'inner',
            )
        )
    libemploi = libemploi[libemploi.annee >= year]
    return libemploi


# 1. Data with libemploi slugified and and associated grade NEG.
libemploi = load_libelles(decennie = 1980, debug = debug)
correspondance_data_frame = get_correspondance_data_frame(which = 'grade')
valid_data_frame = validate_correspondance(correspondance_data_frame, check_only = True)
assert valid_data_frame, 'The correspondace data frame is not valid'

libemploi_grade = (libemploi
        .merge(
            correspondance_data_frame,
            how = 'left',
            left_on = ['statut', 'annee', 'libemploi_slugified'],
            right_on = ['versant', 'annee', 'libelle'],
            )
        .drop('libelle', axis = 1)
        )

len(set(libemploi_grade.grade))

# 2. Adding code netneh
netneh = get_careers(variable = 'c_netneh', decennie = 1980, debug = debug)
netneh = netneh[netneh.annee==2014]
assert (len(netneh.ident) == len(libemploi_grade.ident))


final_merge = (libemploi_grade
        .merge(
            netneh,
            how = 'inner',
            on = ['ident', 'annee'],
            )
        )


check_list = ['ADJOINT ADMINIST HOSP 2EME CL (E03)', 'INFIRMIER DE CLASSE SUPERIEURE(*)']

for gr in check_list:
    filter_gr = final_merge.query('grade == @gr')
    filtered_libemploi = filter_gr.libemploi_slugified
    filtered_netneh = filter_gr.c_netneh
    assert (len(filtered_netneh) == len(filtered_libemploi))
    counts = filtered_netneh.value_counts()
    counts_f = filtered_netneh.value_counts()/len(filtered_netneh)



libelles_emploi_directory = parser.get('correspondances', 'libelles_emploi_directory')

hdf5_file_path = os.path.join(output_directory_path, '1950_1959.h5')


variables_value_count = ['qualite', 'statut', 'etat']

variables_unique = ['ib_', 'c_netneh', 'c_cir', 'libemploi']

variables = ['qualite', 'statut', 'etat', 'ib_', 'c_netneh', 'c_cir', 'libemploi']

store = pd.HDFStstoreore(hdf5_file_path)


def get_df(variable):
    """Recupere une table du store en fonction du nom de la variable"""
    df = pd.read_hdf(hdf5_file_path, variable)
    return df






