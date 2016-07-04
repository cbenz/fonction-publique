from __future__ import division
import os
import pandas as pd

data_path = "C:\Users\lisa.degalle\Documents\Carriere-CNRACL"

#hdf5_file_path = os.path.join(data_path, 'c_g1950_g1959_1.h5')
#read_only_store = pd.HDFStore(hdf5_file_path, 'r')


hdf5_file_path = os.path.join(
    data_path,
    "base_carriere_clean",
    "base_carriere_1",
    )

## Merge by chunk OU
## Random subset OU
##

def get_df(variable1, variable2, condition1, condition2):
    df1 = pd.read_hdf(hdf5_file_path,'{}'.format(variable1), where = condition1, stop = 1000)
    df2 = pd.read_hdf(hdf5_file_path,'{}'.format(variable2), where = condition2, stop = 1000)
    return df1, df2

