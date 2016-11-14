# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 15:54:59 2016

@author: s.rabate


extract_libelle: save a dataframe with all the libellés of all the decennie, 
that will be matched in the grade_matching.py script.

"""

import logging
import os
import pandas as pd
import sys


from fonction_publique.base import clean_directory_path, raw_directory_path, get_careers, parser
from fonction_publique import raw_data_cleaner
from slugify import slugify


libelles_emploi_directory = parser.get('correspondances', 'libelles_emploi_directory')


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


def load_libelles(decennie = None, debug = True, force_recreate = True):
    libemploi = get_careers(variable = 'libemploi', decennie = decennie, debug = debug)
    libemploi['libemploi_slugified'] = libemploi.libemploi.apply(slugify, separator = "_")    
    libemploi = libemploi[libemploi.libemploi != '']
    return libemploi

    
def main():
    debug = False
    # Etape 1: data_cleaning 
    raw_data_cleaner.main(
        raw_directory_path = os.path.join(raw_directory_path, "csv"),
        clean_directory_path = clean_directory_path,
        debug = debug,
        chunksize = None,
        year_min = 2000,
        )
    # Etape 2: extract_libelles and merge
    decennies = [1950, 1970, 1980, 1990]
    for decennie in decennies:
       libemploi = load_libelles(decennie=decennie)
       if decennie == decennies[0]:
           libemploi_all = libemploi
       else: 
           libemploi_all = libemploi_all.append(libemploi)
             
    libemploi_h5 = os.path.join(libelles_emploi_directory,"libemploi.h5")
    libemplois = libemploi_all.groupby(u'annee')['libemploi_slugified'].value_counts()
    log.info("Generating and saving libellés emploi to {}".format(libemploi_h5))
    libemplois.to_hdf(libemploi_h5, 'libemploi')
       
    
if __name__ == "__main__":
    sys.exit(main())    