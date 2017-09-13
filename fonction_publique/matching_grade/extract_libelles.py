#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
extract_libelle: save a dataframe with all the libellés of all the decennie,
that will be matched in the grade_matching.py script.
"""

import logging
import os
import sys


from fonction_publique.base import clean_directory_path, raw_directory_path, get_careers, parser
from fonction_publique import raw_data_cleaner
from slugify import slugify


libelles_emploi_directory = parser.get('correspondances', 'libelles_emploi_directory')


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


def load_libelles(decennie = None, debug = False):
    libemploi = get_careers(variable = 'libemploi', decennie = decennie, debug = debug)
    libemploi['libemploi_slugified'] = libemploi.libemploi.apply(slugify, separator = "_")
    statut = get_careers(variable = 'statut', decennie = decennie, debug = debug)
    libemploi = (libemploi
        .merge(
            statut.query("statut in ['T', 'H']"),
            how = 'inner',
            )
        )
    libemploi = libemploi[libemploi.libemploi != '']
    return libemploi


def main(clean_data = False, debug = False):
    # Etape 1: data_cleaning
    if clean_data:
        raw_data_cleaner.main(
            raw_directory_path = os.path.join(raw_directory_path, "csv"),
            clean_directory_path = clean_directory_path,
            debug = debug,
            chunksize = None,
            year_min = 2000,
            )
    # Etape 2: extract_libelles and merge
    decennies = [1950, 1960, 1970, 1980, 1990]
    for decennie in decennies:
        log.info("Processing decennie {}".format(decennie))
        libemploi = load_libelles(decennie = decennie, debug = debug)
        if decennie == decennies[0]:
            libemploi_all = libemploi
        else:
            libemploi_all = libemploi_all.append(libemploi)

    # Etape 3: save slugified libelles as libemplois
    libemploi_h5 = os.path.join(libelles_emploi_directory, "libemploi.h5")
    libemploi_all.rename(columns = dict(statut = 'versant'), inplace = True)
    libemplois = libemploi_all.groupby([u'annee', u'versant'])['libemploi_slugified'].value_counts()
    log.info("Generating and saving libellés emploi to {}".format(libemploi_h5))
    libemplois.to_hdf(libemploi_h5, 'libemploi')

    # Etape 4: save corresponding bw slug and normal libemploi
    correspondance_libemploi_slug_h5 = os.path.join(libelles_emploi_directory, "correspondance_libemploi_slug.h5")
    correspondance_libemploi_slug = (libemploi_all[[u'versant', u'libemploi', u'annee', u'libemploi_slugified']]
        .drop_duplicates()
        )
    correspondance_libemploi_slug.to_hdf(correspondance_libemploi_slug_h5, 'correspondance_libemploi_slug')


if __name__ == "__main__":
    sys.exit(main(clean_data = False, debug = False))
