from __future__ import division
import os
import pandas as pd
import pylab as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
from openpyxl import Workbook
import numpy as np

data_path = "C:\Users\lisa.degalle\Documents\Carriere-CNRACL"

#hdf5_file_path = os.path.join(data_path, 'c_g1950_g1959_1.h5')
#read_only_store = pd.HDFStore(hdf5_file_path, 'r')


hdf5_file_path = os.path.join(
    data_path,
    "base_carriere_clean",
    "base_carriere_1",
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


pp = PdfPages('descriptive_plots.pdf')



# def rename_variables():

def get_df(variable):
    df = pd.read_hdf(hdf5_file_path,'{}'.format(variable), stop = 1000)
    return df

## Description des variables: value counts, Nan counts, mode des ib par an TO_TEXT
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

## Writing onto text file:
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
        print to_remove_count
        to_remove_count.to_csv(r'variables_count.txt', header=True, index=None, sep=' ', mode='a')
    return True


def get_stat_ib(): # pour IB uniquement
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

## Effectifs par durée d'activité sur la cohorte # etat uniquement
def get_distribution_duree_activite():
    df_etat = get_df('etat')
    df_activite = df_etat.loc[df_etat.etat == '1.0']
    df_activite = df_activite[['ident', 'etat']]
    annee_activite = df_activite.groupby('ident').size().reset_index()
    annee_activite.columns = ['ident', 'nb_annee_activite']
    plt.hist(annee_activite.nb_annee_activite)
    plt.title('Distribution des durees d activite au cours de la carriere (trimestres)')
    plt.save()

## LOOP SUR STATUT QUALITE ETAT
## Evolution des effectifs par an par valeur de chaque variable (moyenne annuelle si la variable est trimestrielle)
def get_effectifs_over_time(variable): # statut, qualite
    df = get_df(variable)
    df_per_year = df.groupby(['annee', variable]).size().reset_index()
    df_per_year.columns = ['annee', '{}_categorie'.format(variable), '{}_compte'.format(variable)]
    sns.pointplot(x="annee", y="{}_compte".format(variable), hue="{}_categorie".format(variable), data=df_per_year)
    plt.title('Effectifs annuels par categorie de la variable {}'.format(variable))
    pp.savefig()


## LOOP SUR IB CODES ET LABEL GRADES
## Effectifs par acte de mobilité déclaré
## (effectifs par nb d'IB / de codes grades / de labels grades uniques sur la carrière)
## Obj. check si les différentes sources de données pour le grade donnent le même nombre de changement
def get_distribution_nb_actes_mobilite(cat):
#    for cat in ['ib_', 'c_netneh', 'c_cir', 'libemploi']:
    df = get_df(cat)
    if cat != 'libemploi_2010_2014':
        df = df.groupby(['ident', '{}'.format(cat)]).size().reset_index()
    else:
        df = df.groupby(['ident', 'libemploi']).size().reset_index()
    df = df.ident.value_counts().reset_index()
    df.columns = ['ident', '{}_count'.format(cat)]

    plt.hist(df['{}_count'.format(cat)], label = '{}'.format(cat))
    plt.title('Effectifs par nombre de {} uniques au cours de la carriere'.format(cat))
    plt.legend()
    pp.savefig()






#def merge(variable1, variable2, trimestre):
#    if trimestre:
#        merged = pd.merge(get_df(variable1), get_df(variable2), on = ["ident", "annee", "trimestre"])
#        merged.to_hdf(
#                    'base_carriere_clean/base_carriere_1_merged', '{}_{}'.format(variable1, variable2),
#                      format = 'table'
#                      )
#    else:
#        merged = pd.merge(get_df(variable1), get_df(variable2), on = ["ident", "annee"])
#        merged.to_hdf(
#            'base_carriere_clean/base_carriere_1_merged', '{}_{}'.format(variable1, variable2),
#              format = 'table'
#              )
#    return 'hourray'
#
#x = get_df('_ib')
#r = np.random.randint(0,81925020,size=10000)