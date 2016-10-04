# -*- coding:utf-8 -*-


from __future__ import division

from fuzzywuzzy import process
import json
import logging
import pandas as pd

from fonction_publique.base import get_careers
from fonction_publique.merge_careers_and_legislation import get_grilles


log = logging.getLogger(__name__)


if __name__ == '__main__':
    decennie = 1970
    libemploi = get_careers(variable = 'libemploi', decennie = decennie).sort_values(['ident', 'annee'])
    grilles = get_grilles()

    libemplois = libemploi.libemploi.value_counts()

    libelles_grade_NEG = sorted(grilles.libelle_grade_NEG.unique().tolist())

    print "Il y a {} libellés emploi différents".format(len(libemplois))
    print "Il y a {} libellés grade NEG différents".format(len(libelles_grade_NEG))

    # libemplois.to_json('libemploi.json', force_ascii = False)

    # with open('libelle_grade_NEG.json', 'w') as output_file:
    #     json.dump(libelles_grade_NEG, output_file, ensure_ascii = False)

    libelles_emploi_by_grade_neg = dict()

    def select_grade_neg(query):
        choices = libelles_grade_NEG
        results = process.extractBests(query, choices, score_cutoff = 90, limit = 500)
        return pd.DataFrame.from_records(results, columns = ['libelle_grade_neg', 'score'])

    def select_libelles_emploi(query = None, choices = libemplois.index):
        assert query is not None
        results = process.extractBests(query, choices, score_cutoff = 90, limit = 500)
        return pd.DataFrame.from_records(results, columns = ['libelle_emploi', 'score'])

    def store_libelle_emploi(libelle_emploi, grade_neg = None):
        assert grade_neg is not None
        if grade_neg in libelles_emploi_by_grade_neg:
            libelles_emploi_by_grade_neg[grade_neg].append(libelle_emploi)  # FIXME: use set union ? 
        else:
            libelles_emploi_by_grade_neg[grade_neg] = [libelle_emploi]

    for libelle_emploi in libemplois.index:
        if libelle_emploi == "":
            log.info("Skipping libelle_emploi = {}")
            continue
        print "libelle emploi: {}".format(libelle_emploi)
        grades_neg = select_grade_neg(libelle_emploi)
        print "Grade NEG possibles:\n{}".format(grades_neg)
        selection = raw_input("selection: ", )
        grade_neg = grades_neg.loc[int(selection), "libelle_grade_neg"]
        print "Le grade NEG suivant a été selectionné: {}".format(grade_neg)
        store_libelle_emploi(libelle_emploi, grade_neg = grade_neg)
        print select_libelles_emploi(query = grade_neg)

        break
