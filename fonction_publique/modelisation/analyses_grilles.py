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
save_path = '/Users/simonrabate/Desktop/IPP/CNRACL/fonction_publique/ecrits/modelisation_carriere/Figures'

def select_grilles(corps):
    path_grilles = os.path.join(
    pkg_resources.get_distribution('fonction_publique').location,
    'fonction_publique',
    'assets',
    'grilles_fonction_publique',
    )
    grilles = pd.read_hdf(os.path.join(path_grilles,"grilles_old.h5"))
    if corps == 'AT':
        libNEG_corps = ['ADJOINT TECHNIQUE DE 2EME CLASSE', 'ADJOINT TECHNIQUE DE 1ERE CLASSE',
                        'ADJOINT TECHNIQUE PRINCIPAL DE 2EME CLASSE', 'ADJOINT TECHNIQUE PRINCIPAL DE 1ERE CLASSE']
    if corps == 'AA':
        libNEG_corps = ['ADJOINT ADMINISTRATIF DE 2EME CLASSE', 'ADJOINT ADMINISTRATIF DE 1ERE CLASSE',
                    'ADJOINT ADMINISTRATIF PRINCIPAL 2E CLASSE', 'ADJOINT ADMINISTRATIF PRINCIPAL 1E CLASSE']
    if corps == 'AS':

        libNEG_corps = ['AIDE SOIGNANT CL NORMALE (E04)', 'AIDE SOIGNANT CL SUPERIEURE (E05)',
                        'AIDE SOIGNANT CL EXCEPT (E06)']
    subset_grilles = grilles[grilles.libelle_grade_NEG.isin(libNEG_corps)]
    return (subset_grilles)

def main():
    for corps in ['AT', 'AA', 'AS']:
        print(corps)
        grille =  select_grilles(corps)
        grille = grille.sort(['code_grade_NEG','echelon'])
        grille.echelon.loc[grille.echelon == 'ES'] = '08'
        grille['date'] = grille.date_effet_grille.dt.year
        grille = grille.loc[grille.date >= 2007]
        grille['date'] = grille['date'].astype(str)
        
        # 1. Ecgelons by neg
        list_neg = grille.code_grade.unique()
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
    
            name = corps + '_' + str(neg) + '_grille_by_neg.pdf'
            

            p.save(filename = os.path.join(save_path, name))

#        p = ggplot(grille, aes(x = 'echelon', y = 'ib', color = 'date')) +\
#            geom_step(size=2) + ylab('Indice') +\
#            theme_bw() +\
#            facet_wrap("libelle_grade_NEG")
#        name = corps + '_grille_by_neg.pdf'
#        p.save(filename = os.path.join(save_path, name))
#    
#        # 2. Echelons by date
#        sub_grille = grille.loc[-grille.date.isin(['2012', '2013'])]
#        list_date = sub_grille.date.unique()
#        for idx, y in enumerate(list_date):
#            g_1 = grille.loc[grille.date == y][["code_grade", "ib" ,"echelon"]].reset_index(drop = True)
#            p = ggplot(aes(x = 'echelon', y = 'ib', color = 'code_grade'), g_1)  +\
#            geom_step(size=3) + ylab('Indice')
#    
#            t =  theme_bw() + theme(axis_title_y = element_text(size=20, text='Indice'), \
#                  axis_text_y  = element_text(size=19, face = 'bold'), \
#                  axis_text_x  = element_text(size=10, face = 'bold'), \
#                  axis_title_x = element_text(size=20, text='Echelon'), \
#                  legend_text = element_text(size=40, face = 'bold'))
#            t._rcParams['font.size'] = 10
#    
#            p = p + t
#    
#            name = str(idx) + '_grille_by_date.pdf'
#            p.save(filename = os.path.join(save_path, name))
#    
#    
#        p = ggplot(sub_grille, aes(x = 'echelon', y = 'ib', color = 'libelle_grade_NEG')) +\
#            geom_step(size=2)  +\
#             +\
#            theme_bw() +\
#            facet_wrap("date")
#        name = corps + '_grille_by_date.pdf'
#        p.save(filename = os.path.join(save_path, name))

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    main()
