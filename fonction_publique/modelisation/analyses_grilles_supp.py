# -*- coding: utf-8 -*-


## Test sur corps des techniciens de la FPT

# Filters: individuals at least one time in the corps


from ggplot import *
import logging
import inspect
import os
import sys
import pkg_resources
import pandas as pd
import numpy as np
#from fonction_publique.base import raw_directory_path, get_careers, parser

#libelles_emploi_directory = parser.get('correspondances', 'libelles_emploi_directory')
save_path = 'U:/Projets/CNRACL/fonction-publique/fonction_publique/ecrits/modelisation_carriere/Figures'
#save_path = '/Users/simonrabate/Desktop/IPP/CNRACL/fonction_publique/ecrits/modelisation_carriere/Figures'



    path_grilles = os.path.join(
    pkg_resources.get_distribution('fonction_publique').location,
    'fonction_publique',
    'assets',
    'grilles_fonction_publique',
    )
    grilles = pd.read_hdf(os.path.join(path_grilles,"grilles.h5"))
    sub_grilles = grilles.loc[grilles.libelle_FP == "FONCTION PUBLIQUE TERRITORIALE"]
    sub_grilles = sub_grilles.loc[grilles.ib == 253]
    sub_grilles =  sub_grilles.loc[sub_grilles.date_effet_grille.dt.year > 1990]


def get_grilles_supp():
    path_grilles = os.path.join(
    pkg_resources.get_distribution('fonction_publique').location,
    'fonction_publique',
    'assets',
    )
    grilles_supp = pd.read_csv(
        os.path.join(path_grilles, "neg_grades_supp.csv"), sep = ";"
        )
    codeNEG_corps = ['0793', '0794', '0795', '0796']

    subset_grilles = grilles_supp[grilles_supp.code_grade_NEG_rempl.isin(codeNEG_corps)]
    neg_supp = subset_grilles.code_grade_NEG.tolist()

    return (neg_supp)




def select_grilles(code_neg):
    path_grilles = os.path.join(
    pkg_resources.get_distribution('fonction_publique').location,
    'fonction_publique',
    'assets',
    'grilles_fonction_publique',
    )
    grilles = pd.read_hdf(os.path.join(path_grilles,"grilles.h5"))
    code_neg = map(int, code_neg)
    code_neg = map(str, code_neg)
   # grilles['neg'] = pd.to_numeric(grilles.code_grade_NEG, errors = "ignored")
   # grilles.loc[grilles.neg.notnull(), "neg"] =  grilles.neg.loc[grilles.neg.notnull()].astype(int)
    subset_grilles = grilles[grilles.code_grade_NEG.isin(code_neg)]
    return (subset_grilles)


def plot_grilles_comp(grille, list_neg, year):
    sub_grille = grille.loc[(grille.date == year) & (grille.code_grade.isin(list_neg))]
    g_1 = sub_grille[["code_grade", "ib" ,"echelon"]].reset_index(drop = True)
    p = ggplot(aes(x = 'echelon', y = 'ib', color = 'code_grade'), g_1)  +\
    geom_step(size=3) + ylab('Indice')

    t =  theme_bw() + theme(axis_title_y = element_text(size=20, text='Indice'), \
          axis_text_y  = element_text(size=19, face = 'bold'), \
          axis_text_x  = element_text(size=10, face = 'bold'), \
          axis_title_x = element_text(size=20, text='Echelon'), \
          legend_text = element_text(size=40, face = 'bold'))
    t._rcParams['font.size'] = 10



def plot_grille_by_date(grille, list_neg, save = True):
    sub_grille = grille.loc[(grille.code_grade.isin(list_neg))]
    p = ggplot(sub_grille, aes(x = 'echelon', y = 'ib', color = 'date')) +\
    geom_step(size=2) + ylab('Indice') +\
    theme_bw() +\
    facet_wrap("libelle_grade_NEG")
    if save:
        name = corps + '_' + str(neg) + '_grille_by_neg.pdf'
        p.save(filename = os.path.join(save_path, name))


def main():

    neg_AT =  ['793', '794', '795', '796']
    neg_supp = get_grilles_supp()
    code_neg = neg_AT + neg_supp

    grille =  select_grilles(code_neg)
    grille['date'] = grille.date_effet_grille.dt.year + (grille.date_effet_grille.dt.month -1)/12
    grille = grille.loc[grille.date >= 1998]
    grille['date'] = grille['date'].astype(str)

    neg_AT1 = ['27', '35', '91', '625', '769']
    neg_AT2 = ['26', '34', '626']
    neg_AT3 = ['25', '33', '627']
    neg_AT4 = ['156', '157', '628']



        # 1. Ecgelons by neg
        list_neg = neg_AT1
        for idx, neg in enumerate(list_neg):
            g_1 = grille.loc[grille.code_grade == neg][["date", "ib" ,"echelon"]].reset_index(drop = True)

            p = ggplot(aes(x = 'echelon', y = 'ib', color = 'date'), g_1)  +\
            geom_step(size=3)

            t =  theme_bw() + theme(axis_title_y = element_text(size=20, text='Indice'), \
                  axis_text_y  = element_text(size=10, face = 'bold'), \
                  axis_text_x  = element_text(size=10, face = 'bold'), \
                  axis_title_x = element_text(size=20, text='Echelon'), \
                  legend_text = element_text(size=40, face = 'bold'))
            t._rcParams['font.size'] = 10

            p = p + t

            name =  str(neg) + '_grille_by_neg.pdf'

            p.save(filename = os.path.join(save_path, name))



        p = ggplot(grille, aes(x = 'echelon', y = 'ib', color = 'date')) +\
            geom_step(size=2) + ylab('Indice') +\
            theme_bw() +\
            facet_wrap("libelle_grade_NEG")
        name = 'AT1' + '_grille_by_neg.pdf'
        p.save(filename = os.path.join(save_path, name))

        # 2. Echelons by date
        sub_grille = grille.loc[-grille.date.isin(['2014', '2015'])]
        list_date = sub_grille.date.unique()
        for idx, y in enumerate(list_date):
            g_1 = grille.loc[grille.date == y][["code_grade", "ib" ,"echelon"]].reset_index(drop = True)
            p = ggplot(aes(x = 'echelon', y = 'ib', color = 'code_grade'), g_1)  +\
            geom_step(size=3) + ylab('Indice')

            t =  theme_bw() + theme(axis_title_y = element_text(size=20, text='Indice'), \
                  axis_text_y  = element_text(size=19, face = 'bold'), \
                  axis_text_x  = element_text(size=10, face = 'bold'), \
                  axis_title_x = element_text(size=20, text='Echelon'), \
                  legend_text = element_text(size=40, face = 'bold'))
            t._rcParams['font.size'] = 10

            p = p + t

            name = y + '_grille_by_date.pdf'
            p.save(filename = os.path.join(save_path, name))


        p = ggplot(sub_grille, aes(x = 'echelon', y = 'ib', color = 'libelle_grade_NEG')) +\
            geom_step(size=2)  +\
             +\
            theme_bw() +\
            facet_wrap("date")
        name = corps + '_grille_by_date.pdf'
        p.save(filename = os.path.join(save_path, name))

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    main()
