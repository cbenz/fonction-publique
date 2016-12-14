# -*- coding: utf-8 -*-

import os
import pandas as pd

from fonction_publique.base import parser
from fonction_publique.matching_grade.extract_libelles import (
    load_libelles,
    )
from fonction_publique.matching_grade.grade_matching import (
    get_correspondance_data_frame,
    )
from fonction_publique.merge_careers_and_legislation import get_grilles


def main():
    debug = True
    decennies = [1950] #, 1960, 1970, 1980, 1990]
    for decennie in decennies:
        print("Processing decennie {}".format(decennie))
        libemploi = load_libelles(decennie = decennie, debug = debug)
        if decennie == decennies[0]:
            libemploi_all = libemploi
        else:
            libemploi_all = libemploi_all.append(libemploi)

    libemploi_cleaned = (libemploi_all[[u'statut', u'libemploi', u'annee', u'libemploi_slugified']]
        .rename(columns = dict(statut = 'versant'))
        .drop_duplicates()
        )

    correspondance_data_frame = get_correspondance_data_frame(which = 'grade').drop('date_effet', axis = 1)
    grilles = get_grilles()

    versants = set(['FONCTION PUBLIQUE HOSPITALIERE', 'FONCTION PUBLIQUE TERRITORIALE'])
    assert set(grilles.libelle_FP.value_counts(dropna = False).index.tolist()) == versants

    grilles['versant'] = 'T'
    grilles.loc[grilles.libelle_FP == "FONCTION PUBLIQUE HOSPITALIERE", 'versant'] = 'H'

    final_correspondance = (correspondance_data_frame
        .merge(
            grilles[['versant', 'libelle_grade_NEG', 'code_grade']].drop_duplicates(),
            how = 'left',
            left_on = ['versant', 'grade'],
            right_on = ['versant', 'libelle_grade_NEG'],
            )
        .drop('grade', axis = 1)
        )

    final = (libemploi_cleaned
        .merge(
            final_correspondance,
            how = 'inner',
            left_on = ['versant', 'annee', 'libemploi_slugified'],
            right_on = ['versant', 'annee', 'libelle'],
            )
        .drop('libelle', axis = 1)
        )

    return final

