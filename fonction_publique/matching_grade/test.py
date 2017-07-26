# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 11:12:12 2017

@author: s.rabate
"""

from __future__ import division

from tabulate import tabulate
import os
import pprint
import sys

import numpy as np
import pandas as pd
from slugify import slugify

from sas7bdat import SAS7BDAT


from fonction_publique.base import raw_directory_path, clean_directory_path, get_careers, parser
from fonction_publique.merge_careers_and_legislation import get_grilles


libelles_emploi_directory = parser.get('correspondances', 'libelles_emploi_directory')
table_cdc_path = "M:/CNRACL/correspondance/LS/2017_lib2014/2017_lib2014.xlsx"


# Original libellés
decennies = [1950, 1960, 1970, 1980, 1990]
for decennie in decennies:
    print("Processing decennie {}".format(decennie))
    libemploi = get_careers(variable = 'libemploi', decennie = decennie, debug = False)
    if decennie == decennies[0]:
        libemploi_all = libemploi[libemploi.annee == 2014]
    else:
        libemploi_all = libemploi_all.append(libemploi[libemploi.annee == 2014])
libemplois2014  = libemploi_all.libemploi.value_counts()
libemplois2014 = pd.DataFrame({'libemploi':libemplois2014.index, 'nb_obs':libemplois2014.values})

# Table CDC
table_cdc = pd.read_excel(table_cdc_path, encoding = 'utf-8')
table_cdc  = table_cdc.sort('nb_obs', ascending=False)

# Merge des deux bases de libellés
data1 = table_cdc.rename(columns={'lib_cir_2014': 'lib_cir_2014', 'nb_obs': 'nb_obs_CDC'})
data1 = data1[['lib_cir_2014', 'nb_obs_CDC']]
data1.lib_cir_2014[data1.lib_cir_2014.isnull()] = ""

data2 = libemplois2014.rename(columns={'libemploi': 'lib_cir_2014', 'nb_obs': 'nb_obs_IPP'})
data2 = data2[['lib_cir_2014', 'nb_obs_IPP']]

data_merge = data1.merge(data2, how = 'outer', on = 'lib_cir_2014')


# Nb de lignes
a = data_merge.nb_obs_CDC.sum()
b = data_merge.nb_obs_IPP.sum()
print("{} lignes dans la base CDC contre {} dans la base IPP".format(a, b))
# Nb de MV
a = sum(data_merge.nb_obs_CDC[data_merge.lib_cir_2014==""])
b = sum(data_merge.nb_obs_IPP[data_merge.lib_cir_2014==""])
print("{} libellés non renseignés dans la base CDC contre {} dans la base IPP".format(a, b))
# Nb de libellés différents
a = len(data_merge.lib_cir_2014[pd.notnull(data_merge.nb_obs_CDC)])
b = len(data_merge.lib_cir_2014[pd.notnull(data_merge.nb_obs_IPP)])
print("{} libellés différents dans la base CDC contre {} dans la base IPP".format(a, b))


data_merge = data_merge.sort("nb_obs_CDC", ascending=False)
print(data_merge[:12])
data_merge = data_merge.sort("nb_obs_IPP", ascending=False)
print(data_merge[:12])


