# -*- coding: utf-8 -*-
"""
Created on Fri May 26 11:19:28 2017

@author: l.degalle
"""
import pandas as pd
import os
from fonction_publique.base import output_directory_path

data_chgmt_2006_2011 = pd.read_csv(os.path.join(
    output_directory_path,
    "base_AT_clean_2006_2011",
    "data_changement_grade_2006_2011_t.csv"
    ))

data_chgmt_2005_2006 = pd.read_csv(os.path.join(
    output_directory_path, "base_AT_clean_2006_2011\data_changement_grade_2005_2006.csv"
        ))

data_chgmt_2000_2006 = pd.read_csv(
        os.path.join(output_directory_path, "base_AT_clean_2000_2005/data_changement_grade_2000_2005.csv")
        )

data_non_chgmt_2000_2006 = pd.read_csv(
        os.path.join(output_directory_path, "base_AT_clean_2000_2005/data_non_changement_grade_2000_2005.csv")
        )

idents = set(
    data_chgmt_2006_2011.ident.unique().tolist() +
    data_chgmt_2005_2006.ident.unique().tolist() +
    data_non_chgmt_2000_2006.ident.unique().tolist() +
    data_non_chgmt_2000_2006.ident.unique().tolist()
    )