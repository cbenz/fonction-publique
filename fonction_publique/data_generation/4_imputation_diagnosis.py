# -*- coding: utf-8 -*-


from __future__ import division
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import operator


data_path = os.path.join("M:/CNRACL/output/filter/data_ATT_2012_filtered_after_duration_var_added_new.csv")
fig_path = os.path.join("Q:/CNRACL/Note CNRACL/Figures")
data = pd.read_csv(data_path).reset_index()


def get_hazards(data_plot, column, idents_keep, grade, duree_min):
    data_plot['temp'] = map(int, data_plot[column].tolist())
    if column == 'count_ident_total':
        cum_diff = []
        if (grade == 'TTH4') & (duree_min == False):
            for i in range(len(range(int(data_plot.annee.min()), (int(data_plot.annee.max()))))):
                data_temp = data_plot.loc[:i]
                cum_diff.append(reduce(operator.sub, data_temp[column]))
        else:
            for i in range(len(range(int(data_plot.annee.min()), (int(data_plot.annee.max()) + 1)))):
                data_temp = data_plot.loc[:i]

                cum_diff.append(reduce(operator.sub, data_temp[column]))
        cum_diff = cum_diff + [len(idents_keep)]
        cum_diff = (list(reversed(cum_diff)))
        del cum_diff[-1]
        data_plot['cum_diff_total'] = cum_diff
    hazard = data_plot['temp'] / data_plot['cum_diff_total']
    del data_plot['temp']
    return hazard



def plot_hazards(data, grade, duree_min):
    if duree_min == True:
        condition = 'max'
    else:
        condition = 'min'
    idents_keep = data.query(
        "(c_cir_2012 == '{}') & (annee_entry_{} != -1)".format(grade, condition)
        ).ident.unique().tolist()
    data_grade = data[data['ident'].isin(idents_keep)]
    data = data_grade.query(
        "(change_grade == True) & (ambiguite == False)"
        ).groupby('annee_entry_{}'.format(condition))['ident'].count().reset_index().rename(
            columns={'ident':'count_ident_total'}
            )
    data_ib_null = data_grade.query(
        "(change_grade == True) & (c_cir == 'autre') & (ib == 0) & (ambiguite == False)"
        ).groupby('annee_entry_{}'.format(condition))['ident'].count().reset_index().rename(
            columns={'ident':'count_ident_ib_bef_null'}
            )
    data_grade_bef_autre_ib_non_null = data_grade.query(
        "(change_grade == True) & (c_cir == 'autre') & (ib != 0) & (ambiguite == False)"
        ).groupby('annee_entry_{}'.format(condition))['ident'].count().reset_index().rename(
            columns={'ident':'count_ident_ib_bef_non_null_grade_autre'})

    data_grade_bef_in_corps = data_grade.query(
        "(change_grade == True) & (c_cir != 'autre') & (ambiguite == False)"
        ).groupby('annee_entry_{}'.format(condition))['ident'].count().reset_index().rename(
            columns={'ident':'count_ident_c_cir_bef_in_corps'})

    if grade == 'TTH1':
       data_plot = data.merge(data_ib_null, on = 'annee_entry_{}'.format(condition)).merge(
               data_grade_bef_autre_ib_non_null, on = 'annee_entry_{}'.format(condition))

    else:
        data_plot = data.merge(data_ib_null, on = 'annee_entry_{}'.format(condition)).merge(
               data_grade_bef_autre_ib_non_null, on = 'annee_entry_{}'.format(condition)).merge(
                       data_grade_bef_in_corps, on = 'annee_entry_{}'.format(condition))
    data_plot['annee'] = data_plot['annee_entry_{}'.format(condition)] - 1
    del data_plot['annee_entry_{}'.format(condition)]
    if grade == 'TTH1':
        data_plot.loc[len(data_plot)] = [len(idents_keep), len(idents_keep), len(idents_keep), 2012]
    else:
        data_plot.loc[len(data_plot)] = [len(idents_keep), len(idents_keep), len(idents_keep), len(idents_keep), 2012]
    data_plot = data_plot.sort_values('annee', ascending = False)
    data_plot['hazard_total'] = get_hazards(data_plot, 'count_ident_total', idents_keep, grade, duree_min)
    data_plot['hazard_ib_bef_null'] = get_hazards(data_plot, 'count_ident_ib_bef_null', idents_keep, grade, duree_min)
    data_plot['hazard_c_cir_bef_autre_ib_bef_non_null'] = get_hazards(
        data_plot, 'count_ident_ib_bef_non_null_grade_autre', idents_keep, grade, duree_min,
        )

    if grade != 'TTH1':
        data_plot['hazard_c_cir_bef_in_corps'] = get_hazards(
            data_plot,
            'count_ident_c_cir_bef_in_corps',
            idents_keep,
            grade,
            duree_min)
    else:
        data_plot['hazard_c_cir_bef_in_corps'] = None
    data_plot = data_plot.query('annee != 2012')
    fig = plt.figure(figsize=(7, 7))
    fig.suptitle("M{}. predicted year of entry, n = {}".format(condition[-2:], len(idents_keep)), fontsize=16)
   # plt.title("according to the {}imal predicted year of entry in grade".format(condition))
    plt.plot(data_plot.annee,
            data_plot.hazard_total,
            'b',
            label = 'All previous positions',
            )
    plt.plot(data_plot.annee,
            data_plot.hazard_ib_bef_null,
            '#87CEFA',
            label = 'Previous IB = 0',
            )
    plt.plot(data_plot.annee,
            data_plot.hazard_c_cir_bef_autre_ib_bef_non_null,
            '#6495ED',
            label = 'Previous IB != 0 and grade in autre',
            )
    plt.plot(data_plot.annee,
            data_plot.hazard_c_cir_bef_in_corps,
            '#5F9EA0',
            label = 'Previous grade in corps',
            )
    plt.show()
    fig.savefig(os.path.join(fig_path, 'hazards_{}_if_annee_{}.pdf'.format(grade, condition)), format='pdf')
    return data_plot



def plot_survival(grade):
    fig = plt.figure(figsize=(7, 5))

    idents_keep = data.query(
        "(c_cir_2012 == '{}')".format(grade)
        ).ident.unique().tolist()
    data_grade = data[data['ident'].isin(idents_keep)]
    data_annee_min = data_grade.query(
        "(change_grade == True)"
        ).groupby('annee_entry_min')['ident'].count().reset_index().rename(
            columns={'ident':'count_ident_total_annee_min', 'annee_entry_min':'annee'}
            )
    data_annee_max = data_grade.query(
        "(change_grade == True)"
        ).groupby('annee_entry_max')['ident'].count().reset_index().rename(
            columns={'ident':'count_ident_total_annee_max', 'annee_entry_max':'annee'}
            )
    data_plot = data_annee_min.merge(data_annee_max, on = 'annee')
    fig.suptitle("{}, n = {}".format(grade, len(idents_keep)), fontsize=16)
    plt.plot(data_plot.annee,
        data_plot.count_ident_total_annee_min,
        '#87CEFA',
        label = 'minimal predicted year of entry',
        )
    plt.plot(data_plot.annee,
        data_plot.count_ident_total_annee_max,
        '#5F9EA0',
        label = 'maximal predicted year of entry',
        )
    if grade == 'TTH1':
        plt.legend(loc=2)
    else:
        None
    plt.show()
    fig.savefig(os.path.join(fig_path, 'survival_{}.pdf'.format(grade)), format = 'pdf')
    return fig

def hist_duree_min_duree_max(data):
    data = data[['ident', 'annee_entry_min', 'annee_entry_max']].drop_duplicates()[[
        'annee_entry_min', 'annee_entry_max'
        ]]
#    data_table = data.groupby(
#        ['annee_entry_min', 'annee_entry_max']).size().unstack('annee_entry_max').fillna(0)
    data['annee_entry_max'] = data['annee_entry_max'].astype(int)
    data['annee_entry_min'] = data['annee_entry_min'].astype(int)
    data['gap'] = data['annee_entry_max'] - data['annee_entry_min']
    data.loc[(data['annee_entry_max'] == -1) | (data['annee_entry_min'] == -1),
        ['gap']
        ] = 10
    fig, ax = plt.subplots()
    plt.hist(data.gap, bins=range(min(data.gap), max(data.gap) + 1, 1), edgecolor = "black", color = '#5F9EA0')

    plt.xticks(np.arange(min(data.gap), max(data.gap)+1, 1.0))
    labels = [item.get_text() for item in ax.get_xticklabels()]
    plt.show()
    fig.savefig(os.path.join(fig_path, 'gap.pdf'), format='pdf')
    return


for grade in ['TTH1', 'TTH2', 'TTH3', 'TTH4']:
    plot_hazards(data, grade, True)
    plot_hazards(data, grade, False)
    #plot_survival(grade)

table_duree_min_duree_max(data)
