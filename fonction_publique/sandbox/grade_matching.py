#!/usr/bin/env python
# -*- coding:utf-8 -*-


from __future__ import division

import logging
import os
import pprint
import sys

import numpy as np
import pandas as pd
from slugify import slugify
from fuzzywuzzy import process

from fonction_publique.base import get_careers, parser, timing
from fonction_publique.merge_careers_and_legislation import get_grilles

try:
    import cPickle as pickle
except:
    import pickle


pd.options.display.max_colwidth = 0
pd.options.display.max_rows = 999

log = logging.getLogger(__name__)


DEBUG = True
VERSANTS = ['T', 'H']


def load_correpondances(correspondances_path = None):
    '''
    Charge la table avec les libellés déjà classés précédemment.
    En l'absence de chemin déclaré pour la table, génère un nouveau dictionnaire dans lequel les grades
    seront renseignés, en recommençant au début.

    Arguments:
        - Chemin pour la table de correspondance
    Sortie:
        - Table de correspondance (chargée, ou nouvelle générée)
    '''
    correspondance_non_available = (
        correspondances_path is None or
        correspondances_path == 'None' or  # None is parsed as string in config.ini
        not os.path.exists(correspondances_path)
        )
    if correspondance_non_available:
        log.info("Il n'existe pas de fichier de correspondances à compléter")
        return dict(zip(VERSANTS, [dict(), dict()]))
    else:
        log.info("Le fichier de correspondances {} est utilisé comme point de départ".format(correspondances_path))
        return pickle.load(open(correspondances_path, "rb"))


def query_grade_neg(query = None, choices = None, score_cutoff = 95):
    '''
    A partir de libelés observés, va chercher les 50 libellés les plus proches dans
    la liste des libellés officiels des grades. En l'absence de résultats, on abaisse le seuil.


    Arguments:
        - Libéllé à classer
        - Liste possible des libellés de grade "officiels"
        - Score
    Sortie:
        - Liste de grade correspondants avec les score de matching associés.
    '''
    assert query is not None
    assert choices is not None
    slugified_choices = [slugify(choice, separator = '_') if (choice is not np.nan) else '' for choice in choices]
    results = process.extractBests(query, slugified_choices, score_cutoff = score_cutoff, limit = 50)
    if results:
        choice_by_slug = dict(zip(slugified_choices, choices))
        data_frame = pd.DataFrame.from_records(results, columns = ['slug_grade_neg', 'score'])
        data_frame['libelle_grade_neg'] = data_frame.slug_grade_neg.map(choice_by_slug)
        return data_frame
    else:
        return query_grade_neg(query, choices = choices, score_cutoff = score_cutoff - 5)


def query_libelles_emploi(query = None, choices = None, last_min_score = 100):
    '''
    A partir du grade attribué à un libellé rentré à la main, cherche parmi autres
    libellés rentrés à la main des correspondances pour le grade choisi.

    Arguments:
        - libellé de grade officiel à rapprocher des libellés
        - Liste possible des libellés rentrés à la main
        - Score
    Sortie:
        - Liste de libellés correspondants avec les score de matching associés.
    '''
    assert query is not None
    assert choices is not None

    slugified_query = slugify(query, separator = '_')
    min_score = 100
    score_cutoff = last_min_score

    empty = True
    extracted_results = process.extractBests(slugified_query, choices, limit = 50)

    while ((min_score >= last_min_score) | empty):
        score_cutoff = score_cutoff - 5
        if score_cutoff < 0:
            log.info("Aucun libellé emploi ne correspondant à {}.".format(query))
            return None
        results = [result for result in extracted_results if result[1] >= score_cutoff]
        if results:
            min_score = min([result[1] for result in results])
            empty = False
        else:
            empty = True
            continue

    log.info("Recherche de libellés emploi correspondant à {}:\n slug: {}\n score >= {}".format(
        query, slugified_query, score_cutoff))
    return pd.DataFrame.from_records(results, columns = ['libelle_emploi', 'score'])


def select_grade_neg(libelle_saisi = None, annee = None, versant = None):
    '''
    Fonction de sélection par l'utilisateur du grade adéquat parmi les choix possibles.
    On charge les grades officiels de l'année courante, puis
    générés par la fonction query_grade_neg. L'utilisateur saisi un unique grade correspondant.
    Si aucun grade ne correspond au libellé considéré, l'utilisateur peut soit abaisser le
    seuil, soit rentrer un grade à la main, soit décider de ne pas classer le grade.

    Arguments:
        - Libellé à classer
        - Année courante
    Sortie:
        - Triplet (versant, grade, date d'effet) correspondant pour le libellé considéré.
    '''
    assert libelle_saisi is not None
    assert annee is not None
    score_cutoff = 95

    grilles = get_grilles(
        date_effet_max = "{}-12-31".format(annee),
        subset = ['libelle_FP', 'libelle_grade_NEG'],
        )
    libelles_grade_NEG = grilles['libelle_grade_NEG'].unique()

    while True:
        grades_neg = query_grade_neg(query = libelle_saisi, choices = libelles_grade_NEG, score_cutoff = score_cutoff)
        print("\nGrade NEG possibles pour {} (score_cutoff = {}):\n{}".format(libelle_saisi, score_cutoff, grades_neg))
        selection = raw_input("""
Present: entrer un NOMBRE
Non present: plus de choix (n), rentrer a la main (m)
Autre: classer comme corps (c), grade suivant (g) , quitter(q)
selection: """)
        if selection == "q":
            return
        elif selection == "g":
            return "next"
        elif selection == "n":
            score_cutoff -= 5
            continue
        elif selection == "m":
            grade_neg = hand_select_grade(
                libelle_a_saisir = libelle_saisi, choices = libelles_grade_NEG, annee = annee)
            break
        elif selection == "c":
            corps = select_corps()
            break
        elif selection.isdigit() and int(selection) in grades_neg.index:
            grade_neg = grades_neg.loc[int(selection), "libelle_grade_neg"]
            break
        else:
            print('Plage de valeurs incorrecte')
            continue

    if selection == "c":
        return ("corps", versant, corps)  # TODO improve
    else:
        date_effet_grille = grilles.loc[
            grilles.libelle_grade_NEG == grade_neg
            ].date_effet_grille.min().strftime('%Y-%m-%d')
        versant = grilles.loc[grilles.libelle_grade_NEG == grade_neg].libelle_FP.unique().squeeze().tolist()
        versant = 'T' if versant == 'FONCTION PUBLIQUE TERRITORIALE' else 'H'  # TODO: clean this mess

    assert versant in VERSANTS, "versant {} is not in {}".format(versant, VERSANTS)
    print("""Le grade NEG suivant a été sélectionné:
 - versant: {}
 - libellé du grade: {}
 - date d'effet la plus ancienne: {}""".format(
        versant,
        grade_neg,
        date_effet_grille,
        ))
    return (versant, grade_neg, date_effet_grille)


def hand_select_grade(libelle_a_saisir = None, choices = None, annee = None):
    '''
    Fonction de sélection par l'utilisateur du grade adéquat pour le libellé donné.
    L'utilisateur saisi à la main un grade, et on cherche dans la liste officielle
    le grade qui s'en rapproche le plus pour confirmation.

    Arguments:
        - Libellé à classer
        - Libelé
        - Année courante
    Sortie:
        - Libellé du grade officiel
    '''
    assert libelle_a_saisir is not None
    assert annee is not None
    score_cutoff = 95

    while True:
        print("Saisir un libellé à la main pour {}:".format(libelle_a_saisir))
        libelle_saisi = raw_input("""
SAISIR UN LIBELLE, quitter (q)
selection: """)
        if libelle_saisi == "q":
            return
        else:
            print("Libellé saisi: {}".format(libelle_saisi))
            selection = raw_input("""
LIBELLE OK (o), RECOMMENCER LA SAISIE (r)
selection: """)
            if selection not in ["o", "q", "r"]:
                print('Plage de valeurs incorrecte (choisir o ou r)')
            elif selection == "r":
                continue
            elif selection == "o":
                grades_neg = query_grade_neg(query = libelle_saisi, choices = choices, score_cutoff = score_cutoff)
                print("\nGrade NEG possibles pour {} (score_cutoff = {}):\n{}".format(
                    libelle_saisi, score_cutoff, grades_neg))
                selection2 = raw_input("""
NOMBRE, recommencer la saisie(r), quitter (q)
selection: """)
                if selection2 == "q":
                    return
                elif selection2 == "r":
                    continue
                elif selection2.isdigit() and int(selection2) in grades_neg.index:
                    grade_neg = grades_neg.loc[int(selection2), "libelle_grade_neg"]
                    return grade_neg


def select_corps(versant = None):
    '''
    Sélectionne le corps dans la liste des corps dans le versant idoine

    Parameters
    ----------
    versant : str, 'H' ou 'T' indispensable

    Return
    ------
    corps: str, le coprs
    '''
    # Provisoire: on regroupe les libellés que l'on souhaite classer comme corps dans
    # un grade ad hoc 'to_match_to_corps' pour chaque versant.
    # A modifier quand on obtient la liste des corps.
    corps = 'corps'
    return corps


def select_libelles_emploi(grade_triplet = None, libelles = None):
    '''
    Sélectionne par l'utilisateur des libellés pouvant être rattaché au grade
    choisi par la fonction select_grade_neg.

    Arguments
    ---------
    grade_triplet : tuple (versant, annee, grade), grade de la nomenclature choisi à l'étape précédente
    libelles :  list, libellés non classés

    Return
    ------
    libelles_emploi_selectionnes : liste des libellés additionnels pouvant être rattachés au triplet précédent
    next_grade : bool, passage au grade suivant
    '''
    assert grade_triplet is not None  # (versant, libelle_grade, date_effet_grille)
    assert libelles is not None
    libelles_emploi_selectionnes = list()
    libelles_init = libelles
    next_grade = False
    last_min_score = 100

    while True:
        if libelles_emploi_selectionnes:
            print("libellés emploi sélectionnés:")
            pprint.pprint(libelles_emploi_selectionnes)
            libelles = [libemploi for libemploi in libelles if libemploi not in libelles_emploi_selectionnes]

        libelles_emploi_additionnels = query_libelles_emploi(
            query = grade_triplet[1],
            choices = libelles,
            last_min_score = last_min_score,
            )

        print("\nAutres libellés emploi possibles:\n{}".format(libelles_emploi_additionnels))
        selection = raw_input("""
liste de nombre (ex: 1:4,6,8,10:11), o (tous), n (aucun), r (recommencer selection),
q (quitter/grade suivant), s (sauvegarde et stats)

selection: """)

        if any((c in [str(i) for i in range(0, 10)]) for c in selection):
            if any((c not in [str(i) for i in '0123456789,:']) for c in selection):
                print('Plage de valeurs incorrecte.')
                continue
            for s in selection.split(","):
                if ":" in s:
                    start = int(s.split(":")[0])
                    stop = int(s.split(":")[1])
                else:
                    start = stop = int(s)

                if not (
                    libelles_emploi_additionnels.index[0] <=
                    start <=
                    stop <=
                    libelles_emploi_additionnels.index[-1:]
                        ):
                    print('Plage de valeurs incorrecte.')
                    continue
                else:
                    libelles_emploi_selectionnes += libelles_emploi_additionnels.loc[
                        start:stop, 'libelle_emploi'].tolist()
                    continue

        elif selection == 'o':
            libelles_emploi_selectionnes += libelles_emploi_additionnels.libelle_emploi.tolist()
            continue

        elif selection == 'n':
            last_min_score = libelles_emploi_additionnels.score.min()
            continue

        elif selection == 's':
            break

        elif selection == 'r':
            last_min_score = 100
            libelles = libelles_init
            libelles_emploi_selectionnes = list()
            continue

        elif selection == 'q':
            next_grade = True
            break

        else:
            print('Non valide')
            continue

    return libelles_emploi_selectionnes, next_grade


def store_libelles_emploi(libelles_emploi = None, annee = None, grade_triplet = None, libemplois = None,
        libelles_emploi_by_grade_triplet = None, correspondances_path = None, new_table_name = None):
    '''
    Enregistre des libellés attribués à un triplet (grade, versant, date d'effet) dans la table de correspondance.

    Arguments:
        - Liste des libellés classés à enregistrer
        - Triplet (versant, grade, date) assigné aux libellés à enregistrer
        - Année
        - Dictionnaire de correspondance entre triplet et liste de libellé
        - Chemin de sauvegarde pour la table de correspondance
        - Liste de tous les libellés de l'année (pour le count de la proportion de libellés classés)
    Sortie:
        - Sauvegarde de la nouvelle table de correspondance avec ajout des nouveaux libellés classés.
        Format: dictionnaires imbriquées {versant:{grade:{date d'effet:list de duplets(annee,libellés)}}}
    '''
    assert libelles_emploi, 'libelles_emploi is None or empty'
    assert isinstance(libelles_emploi, list)
    assert grade_triplet is not None and annee is not None
    assert libemplois is not None
    assert libelles_emploi_by_grade_triplet is not None

    versant, grade, date = grade_triplet

    if versant not in libelles_emploi_by_grade_triplet:
        libelles_emploi_by_grade_triplet[versant] = libelles_emploi_by_date_by_grade = dict()
    else:
        libelles_emploi_by_date_by_grade = libelles_emploi_by_grade_triplet[versant]

    if grade not in libelles_emploi_by_date_by_grade:
        libelles_emploi_by_date_by_grade[grade] = libelles_emploi_by_date = dict()
    else:
        libelles_emploi_by_date = libelles_emploi_by_date_by_grade[grade]

    if date not in libelles_emploi_by_date:
        libelles_emploi_by_date[date] = [(annee, libelles_emploi[0])]
    else:
        new_lib = list(set(libelles_emploi))
        new_lib = zip([annee] * len(new_lib), new_lib)
        libelles_emploi_by_date[date] += new_lib

    if DEBUG:
        print("Libellé renseignés")
        pprint.pprint(libelles_emploi_by_grade_triplet)

    print("Libellé renseignés pour le grade {}:".format(grade))
    pprint.pprint(libelles_emploi_by_grade_triplet[versant][grade])

    libemplois_annee = libemplois.loc[annee, versant]
    vides_count = 0 if "" not in libemplois_annee.index else libemplois_annee.loc[""]
    libelles_emploi_deja_renseignes = get_libelles_emploi_deja_renseignes_by_versant(
        libelles_emploi_by_grade_triplet = libelles_emploi_by_grade_triplet,
        versant = versant)[versant]
    selectionnes_weighted_count = libemplois_annee.loc[libelles_emploi_deja_renseignes].sum()
    total_weighted_count = libemplois_annee.sum()
    selectionnes_count = len(libelles_emploi_deja_renseignes)
    total_count = len(libemplois_annee.index)
    print("""
Pondéré:
{0} / {1} = {2:.2f} % des libellés emplois non vides ({3} vides soit {4:.2f} %) sont attribués
""".format(
        selectionnes_weighted_count,
        total_weighted_count,
        100 * selectionnes_weighted_count / total_weighted_count,
        vides_count,
        100 * vides_count / total_weighted_count,
        ))
    print("""
Non pondéré:\n{0} / {1} = {2:.2f} % des libellés emplois  sont attribués
""".format(
        selectionnes_count,
        total_count,
        100 * selectionnes_count / total_count,
        ))

    if new_table_name:
        new_table_name = correspondances_path[:-16] + new_table_name
        pickle.dump(libelles_emploi_by_grade_triplet, open(new_table_name, "wb"))
    else:
        pickle.dump(libelles_emploi_by_grade_triplet, open(correspondances_path, "wb"))


@timing
def load_libelles_emploi_data(decennie = None, debug = False, force_recreate = False):
    assert decennie is not None
    libemploi_h5 = 'libemploi_{}.h5'.format(decennie)

    if os.path.exists(libemploi_h5) and not force_recreate:
        libemplois = pd.read_hdf(libemploi_h5, 'libemploi')
        log.info("Libellés emploi read from {}".format(libemploi_h5))
    else:
        libemploi = get_careers(variable = 'libemploi', decennie = decennie, debug = debug)
        statut = get_careers(variable = 'statut', decennie = decennie, debug = debug)
        libemploi = (libemploi.merge(
            statut.query("statut in ['T', 'H']"),
            how = 'inner',
            ))
        libemploi['libemploi_slugified'] = libemploi.libemploi.apply(slugify, separator = "_")
        libemploi.rename(columns = dict(statut = 'versant'), inplace = True)
        libemplois = libemploi.groupby([u'annee', u'versant'])['libemploi_slugified'].value_counts()
        log.info("Generating and saving libellés emploi to {}".format(libemploi_h5))
        libemplois.to_hdf(libemploi_h5, 'libemploi')
    return libemplois


def get_libelles_emploi_deja_renseignes_by_versant(libelles_emploi_by_grade_triplet = None, versant = None):
    '''
    Compte des libellés déjà enregistrés dans la table de correspondance

    Arguments:
        - Base de correspondance déjà remplie.
    Sortie:
        - Liste des libellés renseignés
    '''
    assert libelles_emploi_by_grade_triplet is not None
    versants = ['T', 'H'] if versant is None else [versant]
    result = dict()
    for versant in versants:
        result[versant] = []
        for grade in libelles_emploi_by_grade_triplet.values():
            for date in grade.values():
                liste_libelles = [couple[1] for couple in date.values()[0]]
                result[versant] += liste_libelles
    return result


def initialize_libelles(libemplois = None, annee = None, libelles_emploi_by_grade_triplet = None, versant = None):
    '''
    Fonction d'initialisation des libellés à classer, à partir de la

    Parameters
    ----------
    libemplois : Liste de l'ensemble des libellé
    annee : int, année
    libelles_emploi_by_grade_triplet ! dict, dictionnaire de correspondances
    versant : str, 'H' ou 'T', fonction publique territoriale ou hospitalière

    Return
    ------
    Liste ordonnée (selon le nombre d'occurence) des libellés restant à classer pour une année donnée
    '''
    assert libemplois is not None and annee is not None
    assert libelles_emploi_by_grade_triplet is not None
    libelles_emploi_deja_renseignes = get_libelles_emploi_deja_renseignes_by_versant(
        libelles_emploi_by_grade_triplet = libelles_emploi_by_grade_triplet,
        versant = versant)[versant]
    print(libelles_emploi_deja_renseignes)

    renseignes_count_w = libemplois.loc[annee, versant].loc[libelles_emploi_deja_renseignes].sum()
    total_count_w = libemplois.loc[annee, versant].sum()
    renseignes_count = len(libelles_emploi_deja_renseignes)
    total_count = len(libemplois.loc[annee, versant].index)
    if libelles_emploi_deja_renseignes:
        log.info(
            "Pondére:\n{0} libellés emplois sont déjà renseignés soit {1} / {2} = {3:.2f} %   de l'année".format(
                len(libelles_emploi_deja_renseignes),
                renseignes_count_w,
                total_count_w,
                100 * renseignes_count_w / total_count_w
                )
            )
        log.info(
            "Non pondéré: {0} libellés emplois sont déjà renseignés soit {1} / {2} = {3:.2f} %   de l'année".format(
                len(libelles_emploi_deja_renseignes),
                renseignes_count,
                total_count,
                100 * renseignes_count / total_count
                )
            )
        #
    #
    return (libemplois
            .loc[annee, versant]
            .loc[
                ~libemplois.loc[annee, versant].index.isin(libelles_emploi_deja_renseignes)
                ]
            .index
            .tolist()
            )


def select_and_store(libelle_emploi = None, annee = None, versant = None, libelles_emploi_by_grade_triplet = None, libemplois = None,
        libelles = None, correspondances_path = None):
    grade_triplet = select_grade_neg(
        libelle_saisi = libelle_emploi,
        annee = annee,
        versant = versant,
        )

    if grade_triplet is None:
        return 'break'
    if grade_triplet == "next" or grade_triplet[0] == 'corps':
        return 'continue'

    store_libelles_emploi(
        libelles_emploi = [libelle_emploi],
        annee = annee,
        grade_triplet = grade_triplet,
        libemplois = libemplois,
        libelles_emploi_by_grade_triplet = libelles_emploi_by_grade_triplet,
        correspondances_path = correspondances_path,
        )

    while True:
        libelles_emploi_selectionnes, next_grade = select_libelles_emploi(
            grade_triplet = grade_triplet,
            libelles = libelles
            )
        if libelles_emploi_selectionnes:
            store_libelles_emploi(
                libelles_emploi = libelles_emploi_selectionnes,
                annee = annee,
                grade_triplet = grade_triplet,
                libemplois = libemplois,
                libelles_emploi_by_grade_triplet = libelles_emploi_by_grade_triplet,
                correspondances_path = correspondances_path,
                )
        if next_grade:
            return 'continue'


def main(decennie = None):
    assert decennie is not None
    libemplois = load_libelles_emploi_data(decennie = 1950)

    grilles = get_grilles(subset = ['libelle_FP', 'libelle_grade_NEG'])
    libelles_grade_NEG = sorted(grilles.libelle_grade_NEG.unique().tolist())
    print("Il y a {} libellés emploi différents".format(len(libemplois)))
    print("Il y a {} libellés grade NEG différents".format(len(libelles_grade_NEG)))
    correspondances_path = parser.get('correspondances', 'dat')
    libelles_emploi_by_grade_triplet = load_correpondances(
        correspondances_path = correspondances_path)

    annees = sorted(
        libemplois.index.get_level_values('annee').unique().tolist(),
        reverse = True,
        )

    for annee in annees:
        #
        for versant in ['T', 'H']:
            log.info("On considère les libellés emplois de l'année {} du versant {}".format(annee, versant))
            libelles = initialize_libelles(
                libemplois = libemplois,
                annee = annee,
                versant = versant,
                libelles_emploi_by_grade_triplet = libelles_emploi_by_grade_triplet
                )

            for libelle_emploi in libelles:
                if libelle_emploi == "":
                    log.info("On ignore les libelle_emploi vides")
                    continue
                print("\nlibelle emploi: {}\n".format(libelle_emploi))

                result = select_and_store(
                    libelle_emploi = libelle_emploi,
                    annee = annee,
                    versant = versant,
                    libelles_emploi_by_grade_triplet = libelles_emploi_by_grade_triplet,
                    libemplois = libemplois,
                    libelles = libelles,
                    correspondances_path = correspondances_path,
                    )
                if result == 'continue':
                    continue
                elif result == 'break':
                    break

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
