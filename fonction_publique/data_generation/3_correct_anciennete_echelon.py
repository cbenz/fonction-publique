# -*- coding: utf-8 -*-
import os
import pandas as pd


data = pd.read_csv(
    os.path.join('M:/CNRACL/filter', "data_ATT_2011_filtered_after_duration_var_added.csv"),
    index_col = 0
    )

data.loc[
    (data['annee'] == 2011) & (data['min_mois'] != -1) & (data['anciennete_echelon'] >= data['min_mois']),
    'anciennete_echelon'
    ] = data['min_mois']

