#!/usr/bin/env python
# -*- coding:utf-8 -*-


from __future__ import division


#from biryani.strings import slugify
try:
   import cPickle as pickle
except:
   import pickle
from fuzzywuzzy import process
import logging
import os
import pandas as pd
import pprint
import sys


from fonction_publique.base import get_careers, parser
from fonction_publique.merge_careers_and_legislation import get_grilles


pd.options.display.max_colwidth = 0
pd.options.display.max_rows = 999

log = logging.getLogger(__name__)


VERSANTS = ['FONCTION PUBLIQUE HOSPITALIERE', 'FONCTION PUBLIQUE TERRITORIALE']


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

        
def load_libelles_emploi_data(decennie = None):
    ''' 
    Charge l'ensemble des libellés rentrés à la main que l'on observe dans les données 
    pour les années 2000 à 2014 (pour une décennie donnée). 
    
    Arguments: 
        - Décennie considérée
    Sortie: 
        - Base (?) avec l'ensemble des libellés par années et le nombre d'occurence pour chaque années
    '''
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
    results = process.extractBests(query, choices, score_cutoff = score_cutoff, limit = 50)
    if results:
        return pd.DataFrame.from_records(results, columns = ['libelle_grade_neg', 'score'])
    else:
        return query_grade_neg(query, choices = choices, score_cutoff = score_cutoff - 5)


def query_libelles_emploi(query = None, choices = None, score_cutoff = 95):
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


def select_grade_neg(libelle_saisi = None, annee = None):
    ''' 
    Fonction de sélection par l'utilisateur du grade adéquat parmi les choix possibles.
    On charge les grades officiels de l'année courante, puis
    générés par la fonction query_grade_neg. L'utilisateur saisi un unique grade correspondant. 
    Si aucun grade ne correspond au libellé considéré, l'utilisateur peut soit abaisser le
    seuil soit décider de ne pas classer le grade. 
    
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
        print "\nGrade NEG possibles pour {} (score_cutoff = {}):\n{}".format(libelle_saisi, score_cutoff, grades_neg)
        selection = raw_input("""
NOMBRE, non présent -> plus de choix (n), quitter (q)
selection: """)
        if selection == "q":
            return
        elif selection == "n":
            score_cutoff -= 5
            continue
        elif selection.isdigit() and int(selection) in grades_neg.index:
            grade_neg = grades_neg.loc[int(selection), "libelle_grade_neg"]
            break

    date_effet_grille = grilles.loc[grilles.libelle_grade_NEG == grade_neg].date_effet_grille.min().strftime('%Y-%m-%d')
    versant = grilles.loc[grilles.libelle_grade_NEG == grade_neg].libelle_FP.unique().squeeze().tolist()
    assert versant in VERSANTS
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
    ''' 
    Fonction de sélection par l'utilisateur des libellés pouvant être rattaché au grade 
    choisi par la fonction select_grade_neg. 
    
    Arguments: 
        - Grade choisi à l'étape précédente (select_grade_neg), sous forme de triplet (versant, annee, grade)
        - Liste des libellés non classés
    Sortie: 
        - Liste des libellés additionnels pouvant être rattachés au triplet précédent
    '''
    assert grade_triplet is not None  # (versant, libelle_grade, date_effet_grille)
    assert libemplois is not None
    score_cutoff = 95
    libelles_emploi_selectionnes = list()
    next_grade = False

    while True:
        if libelles_emploi_selectionnes:
            print "libellés emploi sélectionnés:"
            pprint.pprint(libelles_emploi_selectionnes)
            libemplois = [libemploi for libemploi in libemplois if libemploi not in libelles_emploi_selectionnes]

        libelles_emploi_additionnels = query_libelles_emploi(
            query = grade_triplet[1],
            choices = libemplois,
            score_cutoff = score_cutoff
            )
        print "\nAutres libellés emploi possibles:\n{}".format(libelles_emploi_additionnels)
        selection = raw_input("""
Liste de nombre (ex: 1:4,6,8,10:11), o (tous), n (aucun), q (quitter/grade suivant), s (sauvegarde et stats)
selection: """)  # TODO: add a default value to n when enter is hit

            
        if any((c in [str(i) for i in range(0, 10)]) for c in selection):
            if any((c not in [str(i) for i in '0123456789,:']) for c in selection):    
                print 'Plage de valeurs incorrecte.'
                continue
            for  s in selection.split(","):
                if ":" in s:
                    start = int(s.split(":")[0])
                    stop = int(s.split(":")[1])
                    if not (libelles_emploi_additionnels.index[0] <= start <= stop <= libelles_emploi_additionnels.index[-1:]):
                        print 'Plage de valeurs incorrecte.'
                        continue
                    else:
                        libelles_emploi_selectionnes += libelles_emploi_additionnels.loc[start:stop].libelle_emploi.tolist()
                        continue
        
                else: 
                    libelles_emploi_selectionnes += [libelles_emploi_additionnels.loc[int(s)].libelle_emploi]
            

        elif selection == 'o':
            libelles_emploi_selectionnes += libelles_emploi_additionnels.libelle_emploi.tolist()
            continue

        elif selection == 'n':
            score_cutoff -= 5
            continue

        elif selection == 's':
            break

        elif selection == 'q':
            next_grade = True
            break

        else:
            print 'Non valide'
            continue

    return libelles_emploi_selectionnes, next_grade



def store_libelles_emploi(libelles_emploi = None, annee = None, grade_triplet = None, libemplois = None,
        libelles_emploi_by_grade_triplet = None, correspondances_path = None, new=None):
    ''' 
    Enregistrement des libellés attribués à un triplet (grade, versant, date d'effet) dans la table de correspondance. 
    
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
    assert libelles_emploi, 'libemplois is None or empty'
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
        libelles_emploi_by_date[date] = [(annee,libelles_emploi[0])]
    else:
        new_lib = list(set(libelles_emploi))
        new_lib = zip([annee]*len(new_lib),new_lib)  
        libelles_emploi_by_date[date] += new_lib

    pprint.pprint(libelles_emploi_by_grade_triplet)

    vides_count = 0 if "" not in libemplois.index else libemplois.loc[""]
    libelles_emploi_deja_renseignes = get_libelles_emploi_deja_renseignes(
        libelles_emploi_by_grade_triplet = libelles_emploi_by_grade_triplet)
    selectionnes_count = libemplois.loc[libelles_emploi_deja_renseignes].sum()
    total_count = libemplois.sum()
    print "\n{0} / {1} = {2:.2f} % des libellés emplois non vides ({3} vides soit {4:.2f} %) sont attribués\n".format(
        selectionnes_count,
        total_count,
        100 * selectionnes_count / total_count,
        vides_count,
        100 * vides_count / total_count,
        )

    if new :
        newpath = correspondances_load_path[:-16] + new
        pickle.dump(libelles_emploi_by_grade_triplet, open(newpath, "wb"))
    else :    
        pickle.dump(libelles_emploi_by_grade_triplet, open(correspondances_path, "wb"))
        
        
def get_libelles_emploi_deja_renseignes(libelles_emploi_by_grade_triplet = None):
    ''' 
    Compte des libellés déjà enregistrés dans la table de correspondance
    
    Arguments: 
        - Base de correspondance déjà remplie.
    Sortie: 
        - Compte des libellés renseignés
    '''  
    assert libelles_emploi_by_grade_triplet is not None
    result = []
    for grade in libelles_emploi_by_grade_triplet.values():
        print(grade)
        for date in grade.values():
            print(date)
            liste_libelles = [ couple[1] for couple in date.values()[0]]
            result += liste_libelles
    return result


def initialize(libemplois = None, annee = None, libelles_emploi_by_grade_triplet = None):
    ''' 
    Fonction d'initialisation des libellés à classer, à partir de la
    
    Arguments: 
        - Liste de l'ensemble des libellé
        - Année
        - Dictionnaire de correspondance
    Sortie: 
        - Liste ordonnée (selon le nombre d'occurence) des libellés restant à classer pour une année donnée
    '''  
    assert libemplois is not None and annee is not None
    assert libelles_emploi_by_grade_triplet is not None
    libelles_emploi_deja_renseignes = get_libelles_emploi_deja_renseignes(libelles_emploi_by_grade_triplet)
    print libelles_emploi_deja_renseignes
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

    correspondances_path = parser.get('correspondances', 'load')
    libelles_emploi_by_grade_triplet = load_correpondances(
        correspondances_path = correspondances_path)

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
            libelles_emploi_by_grade_triplet = libelles_emploi_by_grade_triplet
            )

        for libelle_emploi in libemplois_annee:
            if libelle_emploi == "":
                log.info("On ignore les libelle_emploi vides")
                continue
            print "\nlibelle emploi: {}\n".format(libelle_emploi)

            grade_triplet = select_grade_neg(
                libelle_saisi = libelle_emploi,
                annee = annee
                )

            if grade_triplet is None:
                break

            store_libelles_emploi(
                libelles_emploi = [libelle_emploi],
                annee = annee,
                grade_triplet = grade_triplet,
                libemplois = libemplois.loc[annee],  # FIXME libelle_emploi
                libelles_emploi_by_grade_triplet = libelles_emploi_by_grade_triplet,
                correspondances_path = correspondances_path,
                )

            while True:
                libelles_emploi_selectionnes, next_grade = select_libelles_emploi(
                    grade_triplet = grade_triplet,
                    libemplois = libemplois_annee
                    )
                if libelles_emploi_selectionnes:
                    store_libelles_emploi(
                        libelles_emploi = libelles_emploi_selectionnes,
                        annee = annee,
                        grade_triplet = grade_triplet,
                        libemplois = libemplois.loc[annee],
                        libelles_emploi_by_grade_triplet = libelles_emploi_by_grade_triplet,
                        correspondances_path = correspondances_path,
                        )
                if next_grade:
                    break
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
