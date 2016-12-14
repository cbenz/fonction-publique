#!/usr/bin/env python
# -*- coding:utf-8 -*-


from __future__ import division

import logging
import numpy as np
import pandas as pd

from fonction_publique.base import parser


log = logging.getLogger(__name__)

correspondance_data_frame_path = parser.get('correspondances', 'h5')
correspondance_1 = pd.read_hdf(correspondance_data_frame_path, 'correspondance')
correspondance_2 = pd.read_hdf('/home/benjello/Téléchargements/correspondances.h5', 'correspondance')


def validate_correspondance_table(correspondance_table):
    if correspondance_table.duplicated().any():
        print("The are {} duplicated lines".format(correspondance_table.duplicated().sum()))
        log.info("Cleaning duplciated data")
        correspondance_table_cleaned = correspondance_table.drop_duplicates()
        counts = correspondance_table_cleaned.groupby(['versant', 'annee', 'libelle']).count()
        # print correspondance_table_cleaned.groupby(['versant', 'annee', 'libelle']).count()
        if counts.max().values.tolist() != [1, 1]:
            erroneous_entry = counts.query('grade > 1 or date_effet > 1').index.tolist()
            print erroneous_entry
            print correspondance_table_cleaned.set_index(['versant', 'annee', 'libelle']).ix[erroneous_entry]



        return correspondance_table_cleaned


for correspondance_table in [correspondance_1, correspondance_2]:
    validate_correspondance_table(correspondance_table)


# conflicting_entries

#df = correspondance_1.merge(correspondance_2, how = 'inner', on = ['versant', 'libelle', 'annee'])
#print df