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
import dateutil.parser as parser

libelles_emploi_directory = parser.get('correspondances', 'libelles_emploi_directory')
save_path = 'U:/Projets/CNRACL/fonction-publique/fonction_publique/ecrits/modelisation_carriere/Figures'

def select_corps():
    path_grilles = os.path.join(
    pkg_resources.get_distribution('fonction_publique').location,
    'fonction_publique',
    'assets',
    'grilles_fonction_publique',
    )
    grilles = pd.read_hdf(os.path.join(path_grilles,"grilles_old.h5"))
    libNEG_corps = ['ADJOINT TECHNIQUE DE 2EME CLASSE', 'ADJOINT TECHNIQUE DE 1ERE CLASSE',
                    'ADJOINT TECHNIQUE PRINCIPAL DE 2EME CLASSE', 'ADJOINT TECHNIQUE PRINCIPAL DE 1ERE CLASSE']
    subset_grilles = grilles[grilles.libelle_grade_NEG.isin(libNEG_corps)]
    return (subset_grilles)

def main():
    grille =  select_corps()
    grille = grille.sort(['code_grade_NEG','echelon'])
    grille.echelon.loc[grille.echelon == 'ES'] = '08'
    grille['date'] = grille.date_effet_grille.dt.year
    grille['date'] = grille['date'].astype(str)
    # 1. Ecgelons by neg
    list_neg = grille.libelle_grade_NEG.unique()
    for idx, neg in enumerate(list_neg):
        g_1 = grille.loc[grille.libelle_grade_NEG == neg][["date", "ib" ,"echelon"]].reset_index(drop = True)
        p = ggplot(aes(x = 'echelon', y = 'ib', color = 'date'), g_1)  +\
        ggtitle (neg) +\
        geom_step(size=2) + ylab('Indice') +\
        theme_bw()

        name = str(idx) + '_grille_by_neg.pdf'
        p.save(filename = os.path.join(save_path, name))

    p = ggplot(grille, aes(x = 'echelon', y = 'ib', color = 'date')) +\
        geom_step(size=2) + ylab('Indice') +\
        theme_bw() +\
        facet_wrap("libelle_grade_NEG")
    name = 'grille_by_neg.pdf'
    p.save(filename = os.path.join(save_path, name))

    # 2. Echelons by date
    sub_grille = grille.loc[-grille.date.isin(['2012', '2013'])]
    p = ggplot(sub_grille, aes(x = 'echelon', y = 'ib', color = 'libelle_grade_NEG')) +\
        geom_step(size=2)  +\
        scale_y_discrete(name = 'Indice', limits = (275, 500), breaks = (275, 500)) +\
        theme_bw() +\
        facet_wrap("date")
    name = 'grille_by_date.pdf'
    p.save(filename = os.path.join(save_path, name))

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    main()
