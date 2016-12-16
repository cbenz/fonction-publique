# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 17:59:30 2016

@author: s.rabate
"""

import pandas as pd

dfIn = pd.DataFrame({u'name': ['Tom', 'Jim', 'Claus'],
                     u'location': ['Amsterdam', ['Berlin','Paris'],
                                   ['Antwerp','Barcelona','Pisa'] ]})

# Methode 1
def expand(row):
    locations = row['location'] if isinstance(row['location'], list) else [row['location']]
    s = pd.Series(row['name'], index=list(set(locations)))
    return s

dfIn.apply(expand, axis=1)
dfIn.apply(expand, axis=1).stack()

dfOut = dfIn.apply(expand, axis=1).stack()
dfOut = dfOut.to_frame().reset_index(level=1, drop=False)
dfOut.columns = ['location', 'name']
dfOut.reset_index(drop=True, inplace=True)
print(dfOut)

# Method 2
import numpy as np
dfIn.loc[:, 'location'] = dfIn.location.apply(np.atleast_1d)
all_locations = np.hstack(dfIn.location)
all_names = np.hstack([[n]*len(l) for n, l in dfIn[['name', 'location']].values])
dfOut = pd.DataFrame({'location':all_locations, 'name':all_names})


dfIn2 = pd.DataFrame({u'lib': ['Tom', 'Jim', 'Claus'],
                     u'annee': [2014, 2013, 2012],
                     u'first_year':[2004,2003, 2000]})
all_years = range(min(dfIn2.first_year), max(dfIn2.annee))




import pandas as pd
df = pd.DataFrame({'N': [1, 1, 2, 3],
                   'start': ['08/01/2014 9:30:02',
                             '08/01/2014 10:30:02',
                             '08/01/2014 12:30:02',
                             '08/01/2014 4:30:02']})
df['start'] = pd.to_datetime(df['start'])
df = df.reindex(np.repeat(df.index.values, df['N']), method='ffill')
df['start'] += pd.TimedeltaIndex(df.groupby(level=0).cumcount(), unit='h')



# BEST METHOD WITH REINDEX

import pandas as pd

idx = pd.date_range('09-01-2013', '09-30-2013')

s = pd.Series({'09-02-2013': 2,
               '09-03-2013': 10,
               '09-06-2013': 5,
               '09-07-2013': 1})
s.index = pd.DatetimeIndex(s.index)

s = s.reindex(idx, fill_value=0)





