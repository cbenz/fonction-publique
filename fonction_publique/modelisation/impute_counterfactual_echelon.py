# -*- coding: utf-8 -*-
"""
Created on Sat Jun 17 13:29:38 2017

@author: l.degalle
"""

import os
import pandas as pd
from fonction_publique.base import output_directory_path

data = pd.read_csv(os.path.join(
    output_directory_path,
    "clean_data_finalisation",
    "data_ATT_2002_2015_with_filter_on_etat_at_exit_and_change_to_filter_on_etat_quarterly.csv")
    )

data_non_censored = data.query('(right_censored == False) & (annee == last_y_observed_in_grade)')
