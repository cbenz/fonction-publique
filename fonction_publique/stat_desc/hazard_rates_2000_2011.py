# -*- coding: utf-8 -*-
"""
Created on Fri May 26 11:19:28 2017

@author: l.degalle
"""
from __future__ import division
import pandas as pd
import os
from fonction_publique.base import output_directory_path, project_path, grilles
from clean_data_initialisation import clean_careers
import matplotlib.pyplot as plt

data_path = os.path.join(output_directory_path, "clean_data_finalisation", "data_ATT_2002_2015.csv")
data = pd.read_csv(data_path).reset_index()

def plot_hazards(data, grade, grade_bef_autre, ib_bef_null):
    idents_keep = data.query("c_cir_2011 == '{}'".format(grade)).ident.unique().tolist()
    data_grade = data[data['ident'].isin(idents_keep)]
    if grade_bef_autre:
        if ib_bef_null:
            condition = '(ib == 0)'
        else:
            condition = '(ib != 0)'
        idents_keep = data_grade.query(
            "(indicat_ch_grade == True) & (c_cir == 'autre') & {}".format(condition)
            ).ident.unique().tolist()
    else:
        idents_keep = data_grade.query(
            "(indicat_ch_grade == True) & (c_cir != 'autre')"
            ).ident.unique().tolist()
    data = data_grade[data_grade['ident'].isin(idents_keep)]

    annees = data.annee.unique().tolist()
    return data



#def plot_hazards(grade, grade_bef_autre, ib_bef_null):
#
#    idents_keep = data_carrieres_clean.query("(annee == 2011) & (c_cir == '{}')".format(grade)).ident.unique().tolist()
#    data = pd.read_csv(os.path.join(
#        output_directory_path,
#        "imputation", "data_2003_2011_new_method_4.csv"
#        )).reset_index()
#    data = data[data['ident'].isin(idents_keep)]
#
#    if grade_bef_autre:
#        idents_keep = data.query("c_cir == 'autre'").ident.unique()
#        data = data[data['ident'].isin(idents_keep)]
#
#    if ib_bef_null:
#        idents_keep = data.query('ib == 0').ident.unique()
#        data = data[data['ident'].isin(idents_keep)]
#
#    total_2011 = len(data.ident.unique())
#    chgmt_2010 = len(data.query("(annee == 2010) & (indicat_ch_grade) & (ambiguite == False)").ident.unique())
#    chgmt_2009 = len(data.query("(annee == 2009) & (indicat_ch_grade) & (ambiguite == False)").ident.unique())
#    chgmt_2008 = len(data.query("(annee == 2008) & (indicat_ch_grade) & (ambiguite == False)").ident.unique())
#    chgmt_2007 = len(data.query("(annee == 2007) & (indicat_ch_grade) & (ambiguite == False)").ident.unique())
#    chgmt_2006 = len(data.query("(annee == 2006) & (indicat_ch_grade) & (ambiguite == False)").ident.unique())
#    chgmt_2005 = len(data.query("(annee == 2005) & (indicat_ch_grade) & (ambiguite == False)").ident.unique())
#    chgmt_2004 = len(data.query("(annee == 2004) & (indicat_ch_grade) & (ambiguite == False)").ident.unique())
#    chgmt_2003 = len(data.query("(annee == 2003) & (indicat_ch_grade) & (ambiguite == False)").ident.unique())
#    chgmt_2002 = len(data.query("(annee == 2002) & (indicat_ch_grade) & (ambiguite == False)").ident.unique())
#    #chgmt_2001 = len(data.query("(annee == 2001) & (indicat_ch_grade) & (ambiguite == False)").ident.unique())
#    hazards = list(reversed([chgmt_2010/total_2011,
#        chgmt_2009/(total_2011 - chgmt_2010),
#        chgmt_2008/(total_2011 - chgmt_2010 - chgmt_2009),
#        chgmt_2007/(total_2011 - chgmt_2010 - chgmt_2009 - chgmt_2008),
#        chgmt_2006/(total_2011 - chgmt_2010 - chgmt_2009 - chgmt_2008 - chgmt_2007),
#        chgmt_2005/(total_2011 - chgmt_2010 - chgmt_2009 - chgmt_2008 - chgmt_2007 - chgmt_2006),
#        chgmt_2004/(total_2011 - chgmt_2010 - chgmt_2009 - chgmt_2008 - chgmt_2007 - chgmt_2006 - chgmt_2005),
#        chgmt_2003/(total_2011 - chgmt_2010 - chgmt_2009 - chgmt_2008 - chgmt_2007 - chgmt_2006 - chgmt_2005 - chgmt_2004),
#        chgmt_2002/(total_2011 - chgmt_2010 - chgmt_2009 - chgmt_2008 - chgmt_2007 - chgmt_2006 - chgmt_2005 - chgmt_2004 - chgmt_2003)]))
#        #chgmt_2001/(total_2011 - chgmt_2010 - chgmt_2009 - chgmt_2008 - chgmt_2007 - chgmt_2006 - chgmt_2005 - chgmt_2004 - chgmt_2003 - chgmt_2002)]))
#    year = range(2002, 2011)
#    plt.plot(year, hazards)
#    plt.suptitle(u"Grade:{}, Grade precedent autre: {}, IB precedent nul:{}".format(
#        grade, grade_bef_autre, ib_bef_null))
#    plt.savefig(os.path.join(project_path, 'imputation_duree_grade', 'grade{}_gradebef{}_ibbef{}.png'.format(
#        grade, grade_bef_autre, ib_bef_null)))
#
#plot_hazards('TTH1', True, True)
#plot_hazards('TTH1', False, False)
#plot_hazards('TTH1', True, False)