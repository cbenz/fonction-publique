#! /usr/bin/env python
# -*- coding:utf-8 -*-


from __future__ import division

import logging
import os
import sys

import pandas as pd
from fuzzywuzzy import process

from fonction_publique.base import get_careers
from fonction_publique.merge_careers_and_legislation import get_grilles

pd.options.display.max_colwidth = 0
pd.options.display.max_rows = 999

log = logging.getLogger(__name__)


def query_grade_neg(query = None, choices = None, score_cutoff = 95):
    assert query is not None
    assert choices is not None
    results = process.extractBests(query, choices, score_cutoff = score_cutoff, limit = 50)
    if results:
        return pd.DataFrame.from_records(results, columns = ['libelle_grade_neg', 'score'])
    else:
        return query_grade_neg(query, choices = choices, score_cutoff = score_cutoff - 5)


def query_libelles_emploi(query = None, choices = None, score_cutoff = 95):
    assert query is not None
    assert choices is not None
    if score_cutoff < 0:
        log.info("Aucun libellé emploi ne correspondant à {}.".format(query))
        return None

    log.info("Recherche de libellé emplois correspondant à {} pour un score >= {}".format(
        query, score_cutoff))
    results = process.extractBests(query, choices, score_cutoff = score_cutoff, limit = 50)

    if results:
        return pd.DataFrame.from_records(results, columns = ['libelle_emploi', 'score'])
    else:
        return query_libelles_emploi(query, choices = choices, score_cutoff = score_cutoff - 5)


def select_grade_neg(libelle_saisi = None, libelles_grade_NEG = None, libemplois = None):
    assert libelle_saisi is not None
    assert libelles_grade_NEG is not None
    assert libemplois is not None
    score_cutoff = 95
    while True:
        grades_neg = query_grade_neg(query = libelle_saisi, choices = libelles_grade_NEG, score_cutoff = score_cutoff)
        print "Grade NEG possibles:\n{}".format(grades_neg)
        selection = raw_input("""
NOMBRE, non présent -> plus de choix (n), quitter (q)
selection: """)
        if selection == "q":
            return
        elif selection == "n":
            score_cutoff -= 5
        elif selection.isdigit() and int(selection) in grades_neg.index:
            grade_neg = grades_neg.loc[int(selection), "libelle_grade_neg"]
            break

    print "Le grade NEG suivant a été selectionné: {}".format(grade_neg)
    return grade_neg


def select_libelles_emploi(grade_neg = None, libemplois = None):
    assert grade_neg is not None
    assert libemplois is not None
    score_cutoff = 95
    libelles_emploi_selectionnes = list()

    while True:
        if libelles_emploi_selectionnes:
            print "libellés emploi sélectionnés:"
            print libelles_emploi_selectionnes
            libemplois = [libemploi for libemploi in libemplois if libemploi not in libelles_emploi_selectionnes]

        libelles_emploi_additionnels = query_libelles_emploi(
            query = grade_neg,
            choices = libemplois,
            score_cutoff = score_cutoff
            )
        print "Autres libellés emploi possibles:\n{}".format(libelles_emploi_additionnels)
        selection = raw_input("""
NOMBRE_DEBUT:NOMBRE_FIN, o (tous), n (aucun), q (quitter/grade suivant)
selection: """)  # TODO: add a default value to n when enter is hit

        if ":" in selection:  # TODO improve with regexp
            start = int(selection.split(":")[0])
            stop = int(selection.split(":")[1])
            if not (libelles_emploi_additionnels.index[0] <= start <= stop <= libelles_emploi_additionnels.index[-1:]):
                print 'Plage de valeurs incorrecte.'
                continue
            else:
                libelles_emploi_selectionnes += libelles_emploi_additionnels.loc[start:stop].libelle_emploi.tolist()
                continue

        elif selection == 'o':
            #                 more = raw_input("""
            # Voir plus de libellés oui (o) ou non (n)
            # selection (n): """)
            #                 if more == 'o':
            libelles_emploi_selectionnes += libelles_emploi_additionnels.libelle_emploi.tolist()
            #                     score_cutoff -= 5
            continue

        elif selection == 'n':
            libelles_emploi_selectionnes = []
            continue

        elif selection == 'q':
            break

        else:
            print 'Non valide'
            continue

    return libelles_emploi_selectionnes


def store_libelles_emploi(libelles_emploi = None, grade_neg = None, libemplois = None, 
    libelles_emploi_by_grade_neg = None, correspondace_h5 = None):
    assert libelles_emploi is not None
    assert isinstance(libelles_emploi, list)
    assert grade_neg is not None
    assert libemplois is not None
    assert libelles_emploi_by_grade_neg is not None
    if grade_neg in libelles_emploi_by_grade_neg:
        libelles_emploi_by_grade_neg[grade_neg] += libelles_emploi  # FIXME if needed: use set union ?
    else:
        libelles_emploi_by_grade_neg[grade_neg] = libelles_emploi

    vides_count = 0 if "" not in libemplois.index else libemplois.loc[""]
    # Sum over list to concatenate
    selectionnes_count = libemplois.loc[sum(libelles_emploi_by_grade_neg.values(), [])].sum()
    total_count = libemplois.sum()
    print "{0} / {1} = {2:.2f} % des libellés emplois non vides ({3} vides soit {4:.2f} %) sont attribués".format(
        selectionnes_count,
        total_count,
        100 * selectionnes_count / total_count,
        vides_count,vides_count
        100 * vides_count / total_count,
        )
    if correspondace_h5:
        pd.DataFrame.from_dict(libelles_emploi_by_grade_neg).to_hdf(correspondace_h5, 'correspondance')

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

    def load_libelles_emploi(correspondace_h5 = None):
        if correspondace_h5 is None or not os.path.exists(correspondace_h5):
            return dict()
        else:
            return pd.DataFrame.read_hdf(correspondace_h5, 'correspondance')

    libelles_emploi_by_grade_neg = load_libelles_emploi(correspondace_h5 = correspondace_h5)

    annees = sorted(
        libemplois.index.get_level_values('annee').unique().tolist(),
        reverse = True,
        )
    for annee in annees:
        log.info("On considère les libellés emplois de l'année {}".format(annee))
        libemplois_annee = libemplois.loc[annee].index.tolist()
        for libelle_emploi in libemplois_annee:
            if libelle_emploi == "":
                log.info("On ignore les libelle_emploi vides")
                continue
            print ""
            print "libelle emploi: {}".format(libelle_emploi)

            grade_neg = select_grade_neg(
                libelle_saisi = libelle_emploi,
                libelles_grade_NEG = libelles_grade_NEG,
                libemplois = libemplois_annee,
                )
            store_libelles_emploi(
                libelles_emploi = [libelle_emploi],
                grade_neg = grade_neg,
                libemplois = libemplois.loc[annee],
                libelles_emploi_by_grade_neg = libelles_emploi_by_grade_neg,
                )
            libelles_emploi_selectionnes = select_libelles_emploi(
                grade_neg = grade_neg,
                libemplois = libemplois_annee
                )
            store_libelles_emploi(
                libelles_emploi = libelles_emploi_selectionnes,
                grade_neg = grade_neg,
                libemplois = libemplois.loc[annee],
                libelles_emploi_by_grade_neg = libelles_emploi_by_grade_neg,
                )
        break
