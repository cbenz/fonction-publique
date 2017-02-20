# -*- coding: utf-8 -*-


## Test sur corps des techniciens de la FPT

# Filters: individuals at least one time in the corps

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

def select_grilles():
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
    grille =  select_grilles()
    grille.echelon.loc[grille.echelon == 'ES'] = '08'
    # 1. Evo by neg
    list_neg = grille.libelle_grade_NEG.unique()
    for idx, neg in enumerate(list_neg):
        g_1 = grille.loc[grille.libelle_grade_NEG == neg][["date_effet_grille", "ib" ,"echelon"]].reset_index(drop = True)
        g_1['date'] = g_1.date_effet_grille.dt.year
        g_1['date'] = g_1['date'].astype(str)

        p = ggplot(aes(x = 'echelon', y = 'ib', color = 'date'), g_1)  +\
        ggtitle (neg) +\
        geom_step(size=2) + ylab('Indice') +\
        theme_bw()


        name = str(idx) + '_evo_grille.pdf'

        p.save(filename = os.path.join(save_path, name))




    nb_dates =  grille.date_effet_grille.unique()

    df = pd.DataFrame({'a': range(10), 'b': range(5,15), 'c': range(7,17)})
df['x'] = df.index
df = pd.melt(df, id_vars='x')
ggplot(aes(x='x', y='value', color='variable'), df) + \
      geom_line()+\





    grille_by_neg = grille.groupby(['code_grade_NEG'])['date_effet_grille'].value_counts()



    filtered_df = filtered_df.sort(['ident', 'annee'])
ident = filtered_df['ident'].unique()
df_slice = filtered_df.loc[filtered_df['ident']<ident[100]][['ident', 'annee', 'libemploi', 'c_neg', 'change_neg', 'ib', 'echelon']]
df_slice['name'] = ''
p =  ggplot(df_slice, aes('annee', y='ib'))
p = p +\
geom_line() +\
scale_x_discrete(name = 'Annee', labels = (2007, 2015),  breaks = (2007, 2015))   +\
scale_y_discrete(name = 'Indice', limits = (300, 500), breaks = (300, 500))   +\
theme_bw() +\
facet_wrap("ident", nrow = 10, ncol = 10, )


    list_data = ['1960_1965_carrieres.h5','1966_1969_carrieres.h5',
                 '1970_1975_carrieres.h5','1976_1979_carrieres.h5',
                 '1980_1999_carrieres.h5']
    for data in list_data:
        print("Processing data {}".format(data))
        clean_data = cleaning_data(data)
        if data == list_data[0]:
            data_merge = clean_data
        else:
            data_merge = data_merge.append(clean_data)

    path = os.path.join(save_path, "corps1.h5")
    data_merge.to_hdf(path, 'corps1')

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    main()
