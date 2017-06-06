# -*- coding: utf-8 -*-
"""
Created on Mon Jun 05 18:34:04 2017

@author: l.degalle
"""

import pandas as pd
import os
from fonction_publique.base import output_directory_path

data_bef_2011_path = os.path.join(
    output_directory_path,
    "clean_data_finalisation",
    "data_ATT_2002_2015_redef_var.csv"
    )

data = pd.read_csv(data_bef_2011_path)
