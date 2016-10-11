#!/usr/bin/env python
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


def load_correpondances(correspondances_h5 = None):
    if correspondances_h5 is None or not os.path.exists(correspondances_h5):
        log.info("Il n'existe pas de fichier de correspondances à compléter")
        return pd.DataFrame()
    else:
        log.info("Le fichier de correspondances {} est utiliser comme point de départ".format(correspondances_h5))
        return pd.read_hdf(correspondances_h5, 'correspondance')


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


def select_grade_neg(libelle_saisi = None, annee = None, libemplois = None):
    assert libelle_saisi is not None
    assert annee is not None
    assert libemplois is not None
    score_cutoff = 95

    grilles = get_grilles(
        date_effet_max = "{}-12-31".format(annee),
        subset = ['libelle_FP', 'libelle_grade_NEG'],
        )
    libelles_grade_NEG = grilles['libelle_grade_NEG'].unique()

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

    date_effet_grille = grilles.loc[grilles.libelle_grade_NEG == grade_neg].date_effet_grille.min()
    versant = grilles.loc[grilles.libelle_grade_NEG == grade_neg].libelle_FP.unique().squeeze().tolist()
    assert versant in ['FONCTION PUBLIQUE HOSPITALIERE', 'FONCTION PUBLIQUE TERRITORIALE']
    print """Le grade NEG suivant a été selectionné:
 - versant: {}
 - libellé du grade: {}
 - date d'effet la plus ancienne: {}""".format(
        versant,
        grade_neg,
        date_effet_grille,
        )

    return (versant, grade_neg, date_effet_grille)


def select_libelles_emploi(grade_triplet = None, libemplois = None):
    assert grade_triplet is not None  # (versant, libelle_grade, date_effet_grille)
    assert libemplois is not None
    score_cutoff = 95
    libelles_emploi_selectionnes = list()

    while True:
        if libelles_emploi_selectionnes:
            print "libellés emploi sélectionnés:"
            print libelles_emploi_selectionnes
            libemplois = [libemploi for libemploi in libemplois if libemploi not in libelles_emploi_selectionnes]

        libelles_emploi_additionnels = query_libelles_emploi(
            query = grade_triplet[1],
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
            libelles_emploi_selectionnes += libelles_emploi_additionnels.libelle_emploi.tolist()
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


def store_libelles_emploi(libelles_emploi = None, annee = None, grade_triplet = None, libemplois = None,
        libelles_emploi_by_grade_neg = None, correspondances_h5 = None):
    assert libelles_emploi, 'libemplois is None or empty'
    assert isinstance(libelles_emploi, list)
    assert grade_triplet is not None and annee is not None
    assert libemplois is not None
    assert libelles_emploi_by_grade_neg is not None
    if grade_triplet in libelles_emploi_by_grade_neg:
        updated_grade_triplet_dataframe = pd.DataFrame(
            data = libelles_emploi_by_grade_neg[grade_triplet].values.tolist() + libelles_emploi,
            columns = [grade_triplet],
            )
        if len(libelles_emploi_by_grade_neg.columns) == 1:
            libelles_emploi_by_grade_neg = updated_grade_triplet_dataframe
            raw_input('len = 1')
            print libelles_emploi_by_grade_neg
        else:
            libelles_emploi_by_grade_neg = pd.concat([
                libelles_emploi_by_grade_neg.drop(grade_triplet, axis = 1),  # Exclusion du grade_triplet existant
                updated_grade_triplet_dataframe,
                ])
            raw_input('concat')
            print libelles_emploi_by_grade_neg

        #
    else:
        libelles_emploi_by_grade_neg[grade_triplet] = libelles_emploi
        raw_input('new grade triplet')
        print libelles_emploi_by_grade_neg

    vides_count = 0 if "" not in libemplois.index else libemplois.loc[""]
    # Sum over list to concatenate
    selectionnes_count = libemplois.loc[sum(libelles_emploi_by_grade_neg.values.tolist(), [])].sum()
    print sum(libelles_emploi_by_grade_neg.values.tolist(), [])
    raw_input("Pause")
    total_count = libemplois.sum()
    print "{0} / {1} = {2:.2f} % des libellés emplois non vides ({3} vides soit {4:.2f} %) sont attribués".format(
        selectionnes_count,
        total_count,
        100 * selectionnes_count / total_count,
        vides_count,
        100 * vides_count / total_count,
        )
    if correspondances_h5:
        print pd.DataFrame.from_dict(libelles_emploi_by_grade_neg)
        pd.DataFrame.from_dict(libelles_emploi_by_grade_neg).to_hdf(correspondances_h5, 'correspondance')


def load_libelles_emploi_data(decennie = None):
    assert decennie is not None
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

    return libemplois


def initialize(libemplois = None, annee = None, libelles_emploi_by_grade_neg = None, correspondances_h5 = None):
    assert libemplois is not None and annee is not None
    assert libelles_emploi_by_grade_neg is not None
    libelles_emploi_deja_renseignes = sum(libelles_emploi_by_grade_neg.values.tolist(), [])
    renseignes_count = libemplois.loc[annee].loc[libelles_emploi_deja_renseignes].sum()
    total_count = libemplois.loc[annee].sum()
    if libelles_emploi_deja_renseignes:
        log.info(
            "{0} libellés emplois sont déjà renseignés soit {1} / {2} = {3:.2f} %   de l'année".format(
                len(libelles_emploi_deja_renseignes),
                renseignes_count,
                total_count,
                100 * renseignes_count / total_count
                )
            )
        #
    #
    return (libemplois
            .loc[annee]
            .loc[
                ~libemplois.loc[annee].index.isin(libelles_emploi_deja_renseignes)
                ]
            .index
            .tolist()
            )


def main(decennie = None):
    assert decennie is not None
    libemplois = load_libelles_emploi_data(decennie = 1970)

    grilles = get_grilles(subset = ['libelle_FP', 'libelle_grade_NEG'])
    libelles_grade_NEG = sorted(grilles.libelle_grade_NEG.unique().tolist())
    print "Il y a {} libellés emploi différents".format(len(libemplois))
    print "Il y a {} libellés grade NEG différents".format(len(libelles_grade_NEG))

    correspondances_h5 = 'correspondances.h5'
    libelles_emploi_by_grade_neg = load_correpondances(
        correspondances_h5 = correspondances_h5) # .to_dict(orient = 'list')

    annees = sorted(
        libemplois.index.get_level_values('annee').unique().tolist(),
        reverse = True,
        )

    for annee in annees:
        #
        log.info("On considère les libellés emplois de l'année {}".format(annee))
        libemplois_annee = initialize(
            libemplois = libemplois,
            annee = annee,
            libelles_emploi_by_grade_neg = libelles_emploi_by_grade_neg,
            correspondances_h5 = correspondances_h5,
            )

        for libelle_emploi in libemplois_annee:
            if libelle_emploi == "":
                log.info("On ignore les libelle_emploi vides")
                continue
            print ""
            print "libelle emploi: {}".format(libelle_emploi)

            grade_triplet = select_grade_neg(
                libelle_saisi = libelle_emploi,
                annee = annee,
                libemplois = libemplois_annee,
                )

            if grade_triplet is None:
                break

            store_libelles_emploi(
                libelles_emploi = [libelle_emploi],
                annee = annee,
                grade_triplet = grade_triplet,
                libemplois = libemplois.loc[annee],  # FIXME libelle_emploi
                libelles_emploi_by_grade_neg = libelles_emploi_by_grade_neg,
                correspondances_h5 = correspondances_h5,
                )
            libelles_emploi_selectionnes = select_libelles_emploi(
                grade_triplet = grade_triplet,
                libemplois = libemplois_annee
                )
            if libelles_emploi_selectionnes:
                store_libelles_emploi(
                    libelles_emploi = libelles_emploi_selectionnes,
                    annee = annee,
                    grade_triplet = grade_triplet,
                    libemplois = libemplois.loc[annee],
                    libelles_emploi_by_grade_neg = libelles_emploi_by_grade_neg,
                    correspondances_h5 = correspondances_h5,
                    )
            #
        #
        while True:
            selection = raw_input("""
o: passage à l'année suivante. q : quitter
selection: """)
            if selection == "o":
                break
            if selection == "q":
                return
            else:
                continue


if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    main(decennie = 1970)
