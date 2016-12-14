#!/usr/bin/env python
# -*- coding:utf-8 -*-


from __future__ import division

import logging
import numpy as np
import pandas as pd

from fonction_publique.base import parser
from fonction_publique.matching_grade.grade_matching import select_grade_neg, store_libelles_emploi


log = logging.getLogger(__name__)

correspondance_data_frame_path = parser.get('correspondances', 'h5')
correspondance_1 = pd.read_hdf(correspondance_data_frame_path, 'correspondance')
correspondance_2 = pd.read_hdf('C:/Users/s.rabate/Downloads/correspondances.h5', 'correspondance')




def validate_correspondance_table(correspondance_table):
    if correspondance_table.duplicated().any():
        print("The are {} duplicated lines".format(correspondance_table.duplicated().sum()))
        log.info("Cleaning duplciated data")
        correspondance_table_cleaned = correspondance_table.drop_duplicates()
        counts = correspondance_table_cleaned.groupby(['versant', 'annee', 'libelle']).count()
        # print correspondance_table_cleaned.groupby(['versant', 'annee', 'libelle']).count()
        if counts.max().values.tolist() != [1, 1]:
            erroneous_entry = counts.query('grade > 1 or date_effet > 1').index.tolist()
            correct_entry = counts.query('grade == 1 and date_effet == 1').index.tolist()
            print correspondance_table_cleaned.set_index(['versant', 'annee', 'libelle']).ix[erroneous_entry]
            correspondance_table_cleaned = (
                    correspondance_table_cleaned.set_index(['versant', 'annee', 'libelle'])
                    .ix[correct_entry]
                    .reset_index()
                    )
            for libelle in erroneous_entry:
                   grade_triplet = select_grade_neg(
                            versant = libelle[0], annee = libelle[1], libelle_saisi = libelle[2]
                            )
                   correspondance_table_cleaned = correspondance_table_cleaned.append(pd.DataFrame(
            data = [[grade_triplet[0], grade_triplet[1], grade_triplet[2], libelle[1], libelle[2]]],
            columns = ['versant', 'grade', 'date_effet', 'annee', 'libelle']
            ))
        return correspondance_table_cleaned


def validate_tables_to_merge(correspondance_table1, correspondance_table2):



test = validate_correspondance_table(correspondance_2)
print("test that cleaning works")
test2 = validate_correspondance_table(test)



# conflicting_entries

#df = correspondance_1.merge(correspondance_2, how = 'inner', on = ['versant', 'libelle', 'annee'])
#print df