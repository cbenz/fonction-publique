# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 10:11:35 2016

@author: simonrabate

Grade_matching BL (black list): 
En complément du programme de classification des libélés les plus courants, 
liste des libélés ayant des scores très faibles, avec possibilité de 
remplir le libélé à la main. 

Fonctionnement du programme: 
- Liste des libellés à classer à la main (libellés (1) non classés (2) avec un score bas)
- Remplissage du libellés à la main (selon la date d'effet)
- Enregistrement dans la table de correspondance

"""




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

os.chdir("U:/CNRACL/fonction-publique/fonction_publique/sandbox")

from fonction_publique.base import get_careers, parser
from fonction_publique.merge_careers_and_legislation import get_grilles

from grade_matchingSR import get_libelles_emploi_deja_renseignes, load_libelles_emploi_data, store_libelles_emploi, query_grade_neg

pd.options.display.max_colwidth = 0
pd.options.display.max_rows = 999

log = logging.getLogger(__name__)


VERSANTS = ['FONCTION PUBLIQUE HOSPITALIERE', 'FONCTION PUBLIQUE TERRITORIALE']


def load_libelles_restant(correspondances_path = None, annee=None, libemplois=None ):
    ''' 
    Liste des libellés devant être classés à la main. 
    Correspond à l'ensemble des libellés observés, auxquels on retranche les libellés
    déjà renseignés si l'on donne la table de correspondance en input
    
    Arguments: 
        - Chemin pour la table de correspondance
        - Liste de l'ensemble des libellés à classer pour 
    Sortie: 
        - Liste de libellés non classés à renseigner à la main 
    '''
    assert annee is not None
    assert libemplois is not None
    correspondance_non_available = (
        correspondances_path is None or 
        correspondances_path == 'None' or  # None is parsed as string in config.ini
        not os.path.exists(correspondances_path)
        )
    if correspondance_non_available:
        log.info("Pas de fichier de correspondances en input")
        return libemplois
    else:
        log.info("Le fichier de correspondances {} est utilisé comme input".format(correspondances_path))
        correspondance_table =  pickle.load(open(correspondances_path, "rb"))
        classified_libelles = get_libelles_emploi_deja_renseignes(correspondance_table)
        unclassified_libemp = libemplois.loc[annee].loc[~libemplois.loc[annee].index.isin(classified_libelles)].index.tolist()
        return unclassified_libemp
        
        
               

def select_low_score(liste_lib = None, liste_grade = None, score_min = 60):
    ''' 
    Pour la liste de libellés non classés, on calcule le score max de matching 
    avec le liste des grades. On conserve uniquement les libellés avec faible score. 
    Arguments: 
        - Libéllé à classer
        - Liste possible des libellés de grade "officiels" 
        - Score minimal pour être conservé
    Sortie: 
        - Liste de libelles à classer à la main. 
    '''   
    list_max = list()    
    for lib in liste_lib[1:100]:
        list_max += process.extractBests(lib, liste_grade, score_cutoff = 0, limit = 1)
    low_score =   pd.DataFrame(list_max,columns=('lib','score_max'))
    return (low_score[low_score.score_max<=score_min].lib.tolist())
 

def select_grade_neg_byhand(libelle_a_saisir = None, annee = None):
    ''' 
    Fonction de sélection par l'utilisateur du grade adéquat pour le libellé donné. 
    L'utilisateur saisi à la main un grade, et on cherche dans la liste officielle 
    le grade qui s'en rapproche le plus pour confirmation.     
        
    Arguments: 
        - Libellé à classer
        - Année courante
    Sortie: 
        - Triplet (versant, grade, date d'effet) correspondant pour le libellé considéré.
    '''
    assert libelle_a_saisir is not None
    assert annee is not None
    score_cutoff = 95

    grilles = get_grilles(
        date_effet_max = "{}-12-31".format(annee),
        subset = ['libelle_FP', 'libelle_grade_NEG'],
        )
    libelles_grade_NEG = grilles['libelle_grade_NEG'].unique()

    while True:
        print "Saisir un libellé à la main pour {}:".format(libelle_a_saisir)
        libelle_saisi = raw_input("""
SAISIR UN LIBELLE, grade suivant (q)
selection: """)
        if libelle_saisi == "q":
            return
        else:
            print "Libellé saisi: {}".format(libelle_saisi)
            selection = raw_input("""
LIBELLE OK (o), RECOMMENCER LA SAISIE (r),  grade suivant (q)
selection: """)
            if selection not in ["o","q","r"]:    
                print 'Plage de valeurs incorrecte (choisir o, r ou q)' 
            elif selection == "q":
                return
            elif selection == "r":
                continue
            elif selection == "o":
                 grade_correspondant = check_grade_neg(libelle=libelle_saisi,annee=annee)
                 if grade_correspondant is not None:
                    print """Le grade NEG suivant a été selectionné:
                        - versant: {}
                         - libellé du grade: {}
                         - date d'effet la plus ancienne: {}""".format(
                           grade_correspondant[0],
                           grade_correspondant[1],
                           grade_correspondant[2],
                           )
                    return grade_correspondant
                 else:
                     print "\nPas de grade officiel trouvé pour {}".format(selection)   
                     selection = raw_input("""
                     Saisir un nouveau libellé (r), Passer au grade suivant (q)
                     selection: """)
                     if selection not in ["r","q"]:    
                         print 'Réponse incorrecte (r ou q)' 
                     elif selection == "q":
                         return
                     elif selection == "r":
                         continue                   
                    

def check_grade_neg(libelle = None, annee = None):
    ''' 
    (= select_grade_neg dans grade_matching)
    Attribution d'un grade sur la base du libellé saisi.
    '''
    assert libelle_saisi is not None
    assert annee is not None
    score_cutoff = 95

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

    return (versant, grade_neg, date_effet_grille)



def store_libelles_emploi(libelles_emploi = None, annee = None, grade_triplet = None, libemplois = None,
        libelles_emploi_by_grade_triplet = None, correspondances_path = None):
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
        libelles_emploi_by_date[date] = libelles_emploi
    else:
        libelles_emploi_by_date[date] += libelles_emploi
        libelles_emploi_by_date[date] = list(set(libelles_emploi_by_date[date]))

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
    correspondance_available = (correspondances_path is not None and correspondances_path != 'None')
    if correspondance_available:
        pickle.dump(libelles_emploi_by_grade_triplet, open(correspondances_path, "wb"))


def get_libelles_emploi_deja_renseignes(libelles_emploi_by_grade_triplet = None):
    ''' 
    Compte des libellés déjà enregistrés dans la table de correspondance
    
    Arguments: 
        - Dictionnaire de correspondance entre triplet et liste de libellés.
    Sortie: 
        - Compte des libellés renseignés
    '''  
    assert libelles_emploi_by_grade_triplet is not None
    result = []
    for grade in libelles_emploi_by_grade_triplet.values():
        for date in grade.values():
            result += sum(date.values(), [])
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

    correspondances_path = parser.get('correspondances', 'dat')
      
    annees = sorted(
        libemplois.index.get_level_values('annee').unique().tolist(),
        reverse = True,
        )

    for annee in annees:
        #
        log.info("On considère les libellés emplois de l'année {}".format(annee))
        
    
        unregistered_libelles = load_libelles_restant(
                                correspondances_path = correspondances_path,
                                annee=annee,
                                libemplois=libemplois
                                )
        
        lib_to_match_by_hand = select_low_score(liste_lib=unregistered_libelles, liste_grade=libelles_grade_NEG)    

    
        for libelle_emploi in lib_to_match_by_hand:
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

    
