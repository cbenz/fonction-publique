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
import numpy as np

### MINIMUM WORKING EXEMPLE
input_data = pd.DataFrame({u'country': ['France', 'Germany', 'USA'],
                      u'GDP': ['1', '2', '3'],
                      u'last_year': ['2014', '2013', '2012'],
                      u'first_year':['2004','2003', '2000']})


countries = np.repeat(np.array(['France', 'Germany', 'USA']),[11,5,13], axis=0)
GDP  = np.repeat(np.array(['1', '2', '3']),[11,5,13], axis=0)
first_year  = np.repeat(np.array([2004,2009, 2000]),[11,5,13], axis=0)
last_year  = np.repeat(np.array([2014, 2013, 2012]),[11,5,13], axis=0)
year = range(2004,2015) + range(2009,2014) + range(2000,2013)

Out = pd.DataFrame({u'country': countries,
                      u'GDP': GDP,
                      u'year': year,
                      u'last_year': first_year,
                      u'first_year':last_year})
Out.year = Out.year.astype(str)


row = input_data[0:1]
# TEST
def expand(row, expended_data):
    row.index = pd.DatetimeIndex(pd.to_datetime(row.last_year, format = "%Y"))
    end = row.last_year.values[0]
    beg = row.first_year.values[0]
    idx = pd.date_range(beg, end, freq= 'AS')
    exp_row= row.reindex(idx, method='bfill')
    print(exp_row)
    print id(expended_data)
    expended_data.append(exp_row)
    print id(expended_data)
    print(expended_data)
    expended_data.copy()


expended_data = pd.DataFrame(columns = input_data.columns)
for row_index in range(0, len(input_data)):
    expand(input_data[row_index:(row_index+1)], expended_data)

expended_data = pd.DataFrame(columns = input_data.columns)
for row_nb in range(0, len(input_data)):
    row = input_data[row_nb:(row_nb + 1)]
    row.index = pd.DatetimeIndex(pd.to_datetime(row.last_year, format = "%Y"))
    end = row.last_year.values[0]
    beg = row.first_year.values[0]
    idx = pd.date_range(beg, end, freq = 'AS')
    exp_row= row.reindex(idx, method = 'bfill')
    expended_data = expended_data.append(exp_row)
    expended_data['year'] = pd.to_datetime(expended_data.index)
    expended_data['year'].dt.year
