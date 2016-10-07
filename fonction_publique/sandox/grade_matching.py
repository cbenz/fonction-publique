# -*- coding:utf-8 -*-


from __future__ import division

from fuzzywuzzy import process
import logging
import os
import pandas as pd
import sys

from fonction_publique.base import get_careers
from fonction_publique.merge_careers_and_legislation import get_grilles


pd.options.display.max_colwidth = 0


log = logging.getLogger(__name__)


def query_grade_neg(query = None, choices = None, score_cutoff = 95):
    assert query is not None
    assert choices is not None
    results = process.extractBests(query, choices, score_cutoff = score_cutoff, limit = 500)
    if results:
        return pd.DataFrame.from_records(results, columns = ['libelle_grade_neg', 'score'])
    else:
        return query_grade_neg(query, choices = choices, score_cutoff = score_cutoff - 5)


def query_libelles_emploi(query = None, choices = None, score_cutoff = 95):
    assert query is not None
    assert choices is not None
    if score_cutoff < 0:
        log.info("Aucun libellé emploi ne correspondant à {}.".format(
             query, score_cutoff))
        return None

    log.info("Recherche de libellé emplois correspondant à {} pour un score >= {}".format(
        query, score_cutoff))
    results = process.extractBests(query, choices, score_cutoff = score_cutoff, limit = 500)

    if results:
        return pd.DataFrame.from_records(results, columns = ['libelle_emploi', 'score'])
    else:
        return query_libelles_emploi(query, choices = choices, score_cutoff = score_cutoff - 5)


def select_grade_neg(libelle_saisi = None, libelles_grade_NEG = None, libemplois = None):
    assert libelle_saisi is not None
    assert libelles_grade_NEG is not None
    assert libemplois is not None
    grades_neg = query_grade_neg(query = libelle_saisi, choices = libelles_grade_NEG)
    print "Grade NEG possibles:\n{}".format(grades_neg)
    grade_neg_selection = raw_input("selection: ", )
    grade_neg = grades_neg.loc[int(grade_neg_selection), "libelle_grade_neg"]
    print "Le grade NEG suivant a été selectionné: {}".format(grade_neg)
    return grade_neg

libelles_emploi_by_grade_neg = dict()

def store_libelle_emploi(libelle_emploi, grade_neg = None):
    assert grade_neg is not None
    if grade_neg in libelles_emploi_by_grade_neg:
        libelles_emploi_by_grade_neg[grade_neg].append(libelle_emploi)  # FIXME: use set union ?
    else:
        libelles_emploi_by_grade_neg[grade_neg] = [libelle_emploi]



if __name__ == '__main__':

    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    decennie = 1980

    libemploi_h5 = 'libemploi_{}.h5'.format(decennie)
    force = False
    if os.path.exists(libemploi_h5) and not force:
        libemplois = pd.read_hdf(libemploi_h5, 'libemploi')
        log.info("Libellés emploi read from {}".format(libemploi_h5))
    else:
        libemploi = get_careers(variable = 'libemploi', decennie = decennie)
        libemplois = libemploi.groupby(u'annee')['libemploi'].value_counts()
        log.info("Generating and saving libellés emploi to {}".format(libemploi_h5))
        libemplois.to_hdf(libemploi_h5, 'libemploi')

    grilles = get_grilles()
    libelles_grade_NEG = sorted(grilles
        .libelle_grade_NEG
        .unique()
        .tolist()
        )

    print "Il y a {} libellés emploi différents".format(len(libemplois))
    print "Il y a {} libellés grade NEG différents".format(len(libelles_grade_NEG))

    annees = sorted(
        libemplois.index.get_level_values('annee').unique().tolist(),
        reverse = True,
        )

    for annee in annees:
        for libelle_emploi in libemplois.loc[annee].index:

            if libelle_emploi == "":
                log.info("On ignore les libelle_emploi vides")
                continue
            print ""
            print "libelle emploi: {}".format(libelle_emploi)

            # grades_neg = query_grade_neg(query = libelle_emploi)
            grade_neg = select_grade_neg(
                libelle_saisi = libelle_emploi,
                libelles_grade_NEG = libelles_grade_NEG,
                libemplois = libemplois
                )
            store_libelle_emploi(libelle_emploi, grade_neg = grade_neg)
            autres_libelles_emploi = query_libelles_emploi(
                query = grade_neg, choices = libemplois)
            print "Autres libellés emploi possibles:\n{}".format(autres_libelles_emploi)
            autres_libelles_emploi_selection = raw_input("""
NOMBRE_DEBUT:NOMBRE_FIN, o (tous), n (aucun), p (plus)
selection: """)
            if ':' in autres_libelles_emploi_selection:  # TODO improve with regexp
                start = int(autres_libelles_emploi_selection.split(":")[0])
                stop = int(autres_libelles_emploi_selection.split(":")[1])
                if start > stop:
                    print 'boum'
                    break
                selected_autres_libelles_emploi = autres_libelles_emploi.loc[
                    start:stop].libelle_emploi.tolist()
            elif autres_libelles_emploi_selection == 'o':
                selected_autres_libelles_emploi = autres_libelles_emploi.libelle_emploi.tolist()
            elif autres_libelles_emploi_selection == 'n':
                selected_autres_libelles_emploi = []
                print 'bim'
            elif autres_libelles_emploi_selection == 'p':

                print "choix de plus d'autres libelles"
            else:
                print 'INCOHERENT'
            print selected_autres_libelles_emploi

            break

        break

