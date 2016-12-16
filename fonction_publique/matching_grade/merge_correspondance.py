#!/usr/bin/env python
# -*- coding:utf-8 -*-


from __future__ import division

import logging
import pandas as pd

from fonction_publique.base import parser
from fonction_publique.matching_grade.grade_matching import select_grade_neg


log = logging.getLogger(__name__)

correspondance_data_frame_path = parser.get('correspondances', 'h5')
#correspondance_1 = pd.read_hdf(correspondance_data_frame_path, 'correspondance')
#try:
#    correspondance_2 = pd.read_hdf('C:/Users/s.rabate/Downloads/correspondances.h5', 'correspondance')
#except:
#    correspondance_2 = pd.read_hdf('/Users/simonrabate/Downloads/correspondances.h5', 'correspondance')




def validate_tables_to_merge(correspondance_data_frame1, correspondance_data_frame2):
    # 1. conflicting_entries
    df = correspondance_data_frame1.merge(
        correspondance_data_frame2,
        how = 'inner',
        on = ['versant', 'libelle', 'annee']
        )
    if df.duplicated().any():
        print("The are {} duplicated lines".format(df.duplicated().sum()))
        log.info("Cleaning duplciated data")
        df_cleaned = df.drop_duplicates()
    else:
        df_cleaned = df

    erroneous_entry = (df_cleaned.grade_x != df_cleaned.grade_y) | (df_cleaned.date_effet_x != df_cleaned.date_effet_y)
    erroneous_libelles = df_cleaned.libelle[erroneous_entry].tolist()

    new_grades = pd.DataFrame(columns = ['versant', 'grade', 'date_effet', 'annee', 'libelle'])

    for libelle in erroneous_libelles:
        libelle_triplet = correspondance_data_frame1.loc[
            correspondance_data_frame1.libelle == libelle,
            ['versant', 'annee', 'libelle']
            ]
        libelle_triplet = libelle_triplet.head(1).values.tolist()[0]
        grade_triplet = select_grade_neg(
            versant = libelle_triplet[0],
            annee = libelle_triplet[1],
            libelle_saisi = libelle_triplet[2]
            )
        new_grades = new_grades.append(pd.DataFrame(
            data = [[grade_triplet[0], grade_triplet[1], grade_triplet[2], libelle_triplet[1], libelle_triplet[2]]],
            columns = ['versant', 'grade', 'date_effet', 'annee', 'libelle']
            ))

    correspondance_data_frame1_clean = correspondance_data_frame1[
        [lib not in erroneous_libelles for lib in correspondance_data_frame1.libelle]
        ]
    correspondance_data_frame2_clean = correspondance_data_frame2[
        [lib not in erroneous_libelles for lib in correspondance_data_frame2.libelle]
        ]

    df2 = correspondance_data_frame1_clean.merge(
        correspondance_data_frame2_clean,
        how = 'inner',
        on = ['versant', 'libelle', 'annee']
        )

    corre

    len(correspondance_2)
    test = validate_correspondance_data_frame(correspondance_2)
    print("test that cleaning works")
    test2 = validate_correspondance_data_frame(test)

    print( len(correspondance_2), len(test), len(test2) )

    # conflicting_entries

    # df = correspondance_1.merge(correspondance_2, how = 'inner', on = ['versant', 'libelle', 'annee'])
    # print df
