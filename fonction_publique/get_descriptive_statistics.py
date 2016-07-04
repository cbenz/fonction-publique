from __future__ import division
from collections import Counter
import os
import pandas as pd
import pylab as plt
import seaborn as sns
import numpy as np

data_path = "M:\CNRACL\Carriere-CNRACL"

#hdf5_file_path = os.path.join(data_path, 'c_g1950_g1959_1.h5')
#read_only_store = pd.HDFStore(hdf5_file_path, 'r')


""" Ce fichier permet d'effectuer des statistiques descriptives sur les bases carrières de la CNRACL
Son plan est comme suit :

En intro, on trouve les chemins, variables et la fonction permettant de récupérer une table du store hdf
base_carriere_X.

I. Compte des valeurs uniques, des nans, des string vides et des zeros par variable (les résultats sont stockés dans
le fichier texte statistiques_descriptives.txt)

III. Graphiques :
- sur les indices bruts minimum, moyen et maximum par année
- la distribution des états d'activités
- effectifs par valeurs des variables qualite, statut et etat
- nombre d'actes de mobilité (nb d'ib, de codes grades et de libemploi de 2010 à 2014)
"""

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap

hdf5_file_path = os.path.join(
    data_path,
    "base_carriere_clean",
    "base_carriere_2",
    )

variables_value_count = [
            'qualite',
            'statut',
            'etat',
            ]

variables_unique = [
            'ib_',
            'c_netneh',
            'c_cir',
            'libemploi'
            ]

variables =  ['qualite',
            'statut',
            'etat',
            'ib_',
            'c_netneh',
            'c_cir',
            'libemploi'
            ]

def get_df(variable):
    """recupere une table du store base_carriere_2 en fonction du nom de la variable"""
    df = pd.read_hdf(hdf5_file_path,'{}'.format(variable))
    return df

## I. Description des variables: value counts, nan counts, zero counts
######################################################################

# A) Fonctions
def get_value_counts(variable):
    df = get_df(variable)
    return df[variable].value_counts(dropna = False)

def get_count_unique(variable):
    df = get_df(variable)
    return len(df[variable].unique())

def get_counts_var_to_remove(variable):
    df = get_df(variable)
    na_count = df[variable].isnull().sum(axis=0)
    zero_count = df[variable].isin([0, '0.0']).sum(axis=0)
    empty_count = df[variable].isin([""]).sum(axis=0)
    return pd.DataFrame(
        [na_count, zero_count, empty_count],
        [
            '{}_na_count'.format(variable),
            '{}_zero_count'.format(variable),
            '{}_empty_count'.format(variable),
            ],
        )

# B) Ecriture des résultats du 1. dans un fichier texte
def get_all_counts():
    for variable in variables_value_count:
        value_count = get_value_counts(variable).reset_index()
        value_count.columns = ['valeur_var_{}'.format(variable), 'compte_valeur_var_{}'.format(variable)]
        value_count.to_csv(r'variables_count.txt', header=True, index=None, sep=' ', mode='a')

    for variable in variables_unique:
        count = get_count_unique(variable)
        count = ['Nombre de valeurs pour la variable {}'.format(variable), count]
        count = pd.DataFrame(count)
        count.to_csv(r'variables_count.txt', header=True, index=None, sep=' ', mode='a')

    for variable in variables:
        to_remove_count = get_counts_var_to_remove(variable).reset_index()
        to_remove_count.to_csv(r'statistiques_descriptives.txt', header=True, index=None, sep=' ', mode='a')
    return True

## II.
def get_stat_ib(): # pour IB uniquement
    """ graphe ib moyen, minimum et maximum pour chaque annee de 1970 à 2014"""
    df = get_df('ib_')
    df_ib = df[['annee', 'ib_']]
    df_ib = df_ib.groupby(['annee', 'ib_']).size().reset_index() #TOFIX factoriser
    df_ib_max = df_ib.groupby(['annee']).max().reset_index()
    df_ib_max.columns = ['annee', 'ib_max', 'count']
    df_ib_min = df_ib.groupby(['annee']).min().reset_index()
    df_ib_min.columns = ['annee', 'ib_min', 'count']
    df_ib_mean = df_ib.groupby(['annee']).mean().reset_index()
    df_ib_mean.columns = ['annee', 'ib_mean', 'count']
    sns.pointplot(df_ib_max.annee, df_ib_max.ib_max, label = 'max')
    sns.pointplot(df_ib_min.annee, df_ib_min.ib_min, label = 'min', color = 'b')
    sns.pointplot(df_ib_mean.annee, df_ib_mean.ib_mean, label = 'mean', color = 'r')
    plt.legend()
    plt.title('Minimum, maximum et moyenne des indices bruts par annee')

def get_weird_ib_index(distribution):
    """ part des ib supérieurs à 1015 """ # 98564 (nb d'ident ib trimestre)
    if distribution:
        df = pd.read_hdf(hdf5_file_path, 'ib_', columns = ['ident', 'annee', 'ib_'])
        df_indiv_annee = df[df.ib_ > 1015].groupby('ib_').size().reset_index()
        df_indiv_annee.columns = ['ib_', 'compte']
        plt.plot(df_indiv_annee.ib_, df_indiv_annee.compte)
        plt.title('Distribution des ib superieurs a 1015 sur toute la base (en ident-annee-trimestre)')
    else:
        df = pd.read_hdf(hdf5_file_path, 'ib_', where = "annee > 2010", columns = ['ident', 'annee', 'ib_'], start = 1000000)
        df_indiv_annee = df[df.ib_ > 1015].groupby(['ident', 'annee']).size().reset_index()
        return df_indiv_annee.ident.tolist(), df_indiv_annee.annee.tolist()

store = pd.HDFStore(hdf5_file_path)

def get_grades_agents_ib_ouf():
    """ distribution des codes grades des agents dont l'ib est supérieur à 1015, agents hors classe"""
    ids = get_weird_ib_index()[0]
    ans = get_weird_ib_index()[1]
    ans = pd.unique(ans)
    df = store.select('c_netneh', where = 'ident in ids')
    df = df[df['annee'].isin(ans)]
    df = df.c_netneh.reset_index()
    df.columns = ['ident', 'c_netneh']
    df = df.groupby('c_netneh').size().reset_index()
    df.columns = ['c_netneh', 'count_indiv_annee']
    df = df.sort(['count_indiv_annee'], ascending=False)
    df = df.head(10)
    # pour avoir les codes grades les plus fréquents parmis les personnes ayant des ib sup à 1015
    sns.barplot(df.c_netneh, df.count_indiv_annee)
    plt.title('codes grades netneh des agents ayant un ib etranges')

def get_weird_ib_progression():
    """ compte des agents dont la progession de l'IB est douteuse, i.e descendante par moment /!\ attention,
    il se peut que certains ib passent à 0 en cours de carrière et que ce soit normal TOCHECK"""
    df = store.select('ib_', columns = ['ident', 'annee', 'ib_'])
    df = df.transpose()
    return

def get_effectifs_annuels_entre_sort(entre_ou_sort):
    df_etat_activite = store.select('etat', where = 'etat = 1.0', columns = ['ident', 'annee'])
    if entre_ou_sort == 'entree':
        df = df_etat_activite.groupby('ident')['annee'].min()
    else:
        df = df_etat_activite.groupby('ident')['annee'].max()
    df = df.reset_index()
    df.columns = ['ident', 'annee_{}'.format(entre_ou_sort)]
    df = df.groupby('annee_{}'.format(entre_ou_sort)).size().reset_index()
    df.columns = ['annee_{}'.format(entre_ou_sort), 'compte']
    sns.pointplot(df['annee_{}'.format(entre_ou_sort)], df.compte)


## Effectifs par durée d'activité sur la cohorte # etat uniquement
def get_distribution_duree_activite():
    """  donne la distribution des durees d activite (i.e etat == 1)"""
    df_etat = get_df('etat')
    df_activite = df_etat.loc[df_etat.etat == '1.0']
    df_activite = df_activite[['ident', 'etat']]
    annee_activite = df_activite.groupby('ident').size().reset_index()
    annee_activite.columns = ['ident', 'nb_annee_activite']
    plt.hist(annee_activite.nb_annee_activite)
    plt.title('Distribution des durees d activite au cours de la carriere (trimestres)')
    plt.save()

def get_df_ib_condition(condition): #condition : True pour 0 et false pour
    """ dataframe des ib_ egaux à 0"""
    df_ib = get_df('ib_')
    if condition:
        df_ib = df_ib[df_ib.ib_ == 0]
    else:
        df_ib = df_ib[df_ib.ib_.isnull()] #TOFIX
    df_ib = df_ib.groupby(['ident', 'annee']).size().reset_index()
    df_ib.set_index(df_ib.ident, df_ib.annee)
    df_ib = df_ib.groupby(['ident', 'annee']).size().reset_index()
    df_ib.set_index(df_ib.ident, df_ib.annee)
    return df_ib[['ident', 'annee']]

def get_var_ib_null_or_nan(variable, condition): #condition == null ou condition == Nan
    """ voir dans quelles catégories des variables etat, qualite et statut sont les indiv dont l'ib est égal à 0, pour
    comprendre le sens d'un ib égal à 0 et déceler d'éventuelles anomalies."""
    idents_annee = get_df_ib_condition(condition)
    idents = idents_annee['ident'].tolist()
    annees = idents_annee['annee'].tolist()
    df = pd.read_hdf(hdf5_file_path,'{}'.format(variable), where = [pd.Term("ident", "=", idents)], start = 800000, stop = 999999)
    df = df[df['annee'].isin(annees)]
    df_per_year = df.groupby(['annee', variable]).size().reset_index()
    df_per_year.columns = ['annee', '{}_categorie'.format(variable), '{}_compte'.format(variable)]
    sns.pointplot(x="annee", y="{}_compte".format(variable), hue="{}_categorie".format(variable), data=df_per_year)
    plt.title('Effectifs annuels par categorie de la variable {} pour ib {}'.format(variable, condition))


## on veut les nb d'ident qui ont etat == 1, indice_brut  == 0 ou null (nan). on veut leur qualite
## on veut les nb d'ident qui ont qualite == titulaire, etat == activite. on veut leur savoir si ib null ou 0
#
#store = pd.HDFStore(hdf5_file_path)
#ib_null = store.select('ib_', where=['ib_=0'], columns = ['ident', 'annee'], stop = 10000000)
#etat_activite = store.select('etat', where=['etat=1.0'], columns = ['ident', 'annee'], stop = 10000000)
#qualite_titulaire = store.select('qualite', where=['qualite=T'], columns = ['ident', 'annee'], stop = 10000000)
#statut = store.select('statut', where=['statut=T or statut = H'], columns = ['ident', 'annee'], stop = 10000000)
#check_intersection = pd.merge(ib_null, etat_activite, qualite_titulaire)

## III.
## LOOP SUR STATUT QUALITE ETAT
## Evolution des effectifs par an par valeur de chaque variable (moyenne annuelle si la variable est trimestrielle)
def get_effectifs_over_time(variable): # statut, qualite
    """ voir les effectifs par valeur de chaque variable au cours du temps"""
    df = get_df(variable)
    df_per_year = df.groupby(['annee', variable]).size().reset_index()
    df_per_year.columns = ['annee', '{}_categorie'.format(variable), '{}_compte'.format(variable)]
    sns.pointplot(x="annee", y="{}_compte".format(variable), hue="{}_categorie".format(variable), data=df_per_year)
    plt.title('Effectifs annuels par categorie de la variable {}'.format(variable))


## LOOP SUR IB CODES ET LABEL GRADES
## Effectifs par acte de mobilité déclaré
## (effectifs par nb d'IB / de codes grades / de labels grades uniques sur la carrière)
## Obj. check si les différentes sources de données pour le grade donnent le même nombre de changement
def get_distribution_nb_actes_mobilite(cat):
    """ voir le nombre d'acte de mobilité (i.e environ d'uniques c_cir, c_netneh, libemploi et ib_) pour
    connaître le nb d'acte exploitable pour l'étude et déceler des anomalies de c_cir, c_netneh et libemploi"""
#    for cat in ['ib_', 'c_netneh', 'c_cir', 'libemploi']:
    df = get_df(cat)
    df = df[df[cat] != ''] ## drop empty
    if cat != 'libemploi_2010_2014':
        df = df.groupby(['ident', '{}'.format(cat)]).size().reset_index()
    else:
        df = df.groupby(['ident', 'libemploi']).size().reset_index()
    df = df.ident.value_counts().reset_index()
    df.columns = ['ident', '{}_count'.format(cat)]

    plt.hist(df['{}_count'.format(cat)], label = '{}'.format(cat))
    plt.title('Effectifs par nombre de {} uniques au cours de la carriere'.format(cat))
    plt.legend()


def get_carriere_unique(include_empty_state):
    """ Voir le nombre de carrières uniques (liste ordonnée de c_netneh) et les effectifs par nb de carrières uniques"""
    df_grade = store.select('c_netneh', stop = 1000)
    if include_empty_state:
        df_grade = df_grade
    else:
        df_grade = df_grade[df_grade['c_netneh'] != [''] * len(df_grade['c_netneh'])]
    df_grades_uniques = df_grade.groupby(['ident'])['c_netneh'].unique().reset_index()
    df_grades_uniques.columns = ['ident', 'career_netneh']
    dict_uniques_career_effectifs = Counter(str(e) for e in df_grades_uniques['career_netneh'])
    if include_empty_state:
        del dict_uniques_career_effectifs["['']"]
    else:
        dict_uniques_career_effectifs = dict_uniques_career_effectifs
    sns.pointplot(dict_uniques_career_effectifs.keys(), dict_uniques_career_effectifs.values())
#    plt.title('Effectifs par carriere unique, carriere c_netneh vide exclues. Il y a {} c.u. et {} ident. rps. Carriere ac eff max ={}. c_netneh vide inclus :{}"""'.format(
#                                                                len(dict_uniques_career_effectifs),
#                                                                sum((dict_uniques_career_effectifs.values())),
#                                                                max(dict_uniques_career_effectifs,
#                                                                    key=dict_uniques_career_effectifs.get)),
#                                                                include_empty_state
#                                                                )

def dispersion_grade_paths():
    """ connaître la distribution du nombre de grade accessibles à partir d'un grade """
    df_grade = store.select('c_netneh', stop = 1000000)
    df_grade = df_grade[df_grade['c_netneh'] != [''] * len(df_grade['c_netneh'])]
    df_grades_uniques = df_grade.groupby(['ident'])['c_netneh'].unique().reset_index()
    df_grades_uniques.columns = ['ident', 'career_netneh']
    df_careers = pd.DataFrame(df_grades_uniques.career_netneh)
    df_careers
    for i in range(4):
        df_careers['etat_netneh'+str(i)] = df_careers['career_netneh'].str[i]
    df_careers = df_careers.drop('career_netneh', 1)
    df_careers = df_careers.loc[df_careers['etat_netneh1'].notnull() or
                            df_careers['etat_netneh2'].notnull() or
                            df_careers['etat_netneh3'].notnull()]
    return df_careers.head()









