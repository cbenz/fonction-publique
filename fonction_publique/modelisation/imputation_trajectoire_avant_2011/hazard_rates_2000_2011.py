# -*- coding: utf-8 -*-
"""
Created on Fri May 26 11:19:28 2017

@author: l.degalle
"""
import pandas as pd
import os
from fonction_publique.base import output_directory_path
import matplotlib.pyplot as plt

data_chgmt_2006_2011 = pd.read_csv(os.path.join(
    output_directory_path,
    "base_AT_clean_2006_2011",
    "data_changement_grade_2006_2011_t.csv"
    ))

data_non_chgmt_2006_2011 = pd.read_csv(os.path.join(
    output_directory_path,
    "base_AT_clean_2006_2011",
    "data_non_changement_grade_2006_2011_t.csv"
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
    data_chgmt_2000_2006.ident.unique().tolist() +
    data_non_chgmt_2000_2006.ident.unique().tolist()
    )

# Ident ambigus en 2000
idents_to_del = data_non_chgmt_2000_2006.query('ambiguite_2000 == True').ident

# Sans ambiguite
total_2011 = len(
    set(data_chgmt_2006_2011.ident.unique().tolist() + data_non_chgmt_2006_2011.ident.unique().tolist())
    )
chgmt_2010 = len(data_chgmt_2006_2011.query('(ambiguite_2010 == False) & (indicat_ch_grade_2010 == True)').ident.unique())
chgmt_2009 = len(data_chgmt_2006_2011.query('ambiguite_2009 == False & indicat_ch_grade_2009 == True').ident.unique())
chgmt_2008 = len(data_chgmt_2006_2011.query('ambiguite_2008 == False & indicat_ch_grade_2008 == True').ident.unique())
chgmt_2007 = len(data_chgmt_2006_2011.query('ambiguite_2007 == False & indicat_ch_grade_2007 == True').ident.unique())
chgmt_2006 = len(data_chgmt_2006_2011.query('ambiguite_2006 == False & indicat_ch_grade_2006 == True').ident.unique())
chgmt_2005 = len(data_chgmt_2005_2006.query('ambiguite_2005 == False & indicat_ch_grade_2005 == 1').ident.unique())
chgmt_2004 = len(data_chgmt_2000_2006.query('ambiguite_2004 == False & indicat_ch_grade_2004 == 1').ident.unique())
chgmt_2003 = len(data_chgmt_2000_2006.query('ambiguite_2003 == False & indicat_ch_grade_2003 == 1').ident.unique())
chgmt_2002 = len(data_chgmt_2000_2006.query('ambiguite_2002 == False & indicat_ch_grade_2002 == 1').ident.unique())
chgmt_2001 = len(data_chgmt_2000_2006.query('ambiguite_2001 == False & indicat_ch_grade_2001 == 1').ident.unique())

hazards = list(reversed([chgmt_2010/total_2011,
    chgmt_2009/(total_2011 - chgmt_2010),
    chgmt_2008/(total_2011 - chgmt_2010 - chgmt_2009),
    chgmt_2007/(total_2011 - chgmt_2010 - chgmt_2009 - chgmt_2008),
    chgmt_2006/(total_2011 - chgmt_2010 - chgmt_2009 - chgmt_2008 - chgmt_2007),
    chgmt_2005/(total_2011 - chgmt_2010 - chgmt_2009 - chgmt_2008 - chgmt_2007 - chgmt_2006),
    chgmt_2004/(total_2011 - chgmt_2010 - chgmt_2009 - chgmt_2008 - chgmt_2007 - chgmt_2006 - chgmt_2005),
    chgmt_2003/(total_2011 - chgmt_2010 - chgmt_2009 - chgmt_2008 - chgmt_2007 - chgmt_2006 - chgmt_2005 - chgmt_2004),
    chgmt_2002/(total_2011 - chgmt_2010 - chgmt_2009 - chgmt_2008 - chgmt_2007 - chgmt_2006 - chgmt_2005 - chgmt_2004 - chgmt_2003),
    chgmt_2001/(total_2011 - chgmt_2010 - chgmt_2009 - chgmt_2008 - chgmt_2007 - chgmt_2006 - chgmt_2005 - chgmt_2004 - chgmt_2003 - chgmt_2002)]))
year = range(2001, 2011)

plt.plot(year, hazards)
# Durée max