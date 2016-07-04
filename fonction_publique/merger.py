from __future__ import division
import os
import pandas as pd

data_path = "C:\Users\lisa.degalle\Documents\Carriere-CNRACL"

hdf5_file_path = os.path.join(
    data_path,
    "base_carriere_clean",
    "base_carriere_2",
    )

def get_df(variable):
    """recupere une table du store base_carriere_2 en fonction du nom de la variable"""
    df = pd.read_hdf(hdf5_file_path,'{}'.format(variable), stop = 1000)
    return df

def get_grades_agents_ib_ouf():
