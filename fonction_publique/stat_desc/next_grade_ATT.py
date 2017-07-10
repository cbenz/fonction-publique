# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 09:57:43 2017

@author: l.degalle
"""

from __future__ import division
import matplotlib.pyplot as plt
import numpy as np


save_path = "C:\Users\l.degalle\CNRACL\fonction-publique\fonction_publique\ecrits\descriptive statistics multinomial\Figures"

#
def plot_frequency_next_grade():
    for grade in ['TTH1', 'TTH2', 'TTH3', 'TTH4']:
        data_grade = []
        for annee in range(2011, 2015):
            data_annee = data_long_w_echelon_IPP_corrected.query(
                "(last_y_observed_in_grade == @annee) & (right_censored == False) & (c_cir_2011 == @grade) & (annee == last_y_observed_in_grade) & (quarter == 4)"
                ).next_grade_corrected.value_counts().reset_index().rename(
                        columns = {'index':'next_grade_corrected', 'next_grade_corrected':'count'}
                        )
            data_annee_stay = len(data_long_w_echelon_IPP_corrected.query(
                "(annee == @annee) & (right_censored == False) & (c_cir_2011 == @grade) & (quarter == 4) & (last_y_observed_in_grade != @annee)"
                ).ident.unique()
                )
            data_annee = data_annee.append(
                pd.DataFrame([grade, data_annee_stay]).transpose().rename(columns = {0:'next_grade_corrected', 1:'count'})
                )
            data_annee['share'] = data_annee['count'] / data_annee['count'].sum()
            data_annee = data_annee.sort_values(by = 'share', ascending = False)
            data_annee['cum_share'] = data_annee['share'].cumsum()
            data_annee['last_y_obs'] = annee
            if grade == 'TTH1':
                part_max_des_agents_rep = 0.97
            else:
                part_max_des_agents_rep = 0.99
            data_annee_more_90_percent = data_annee.query('cum_share <= @part_max_des_agents_rep').copy()
            fig, ax = plt.subplots()
            print data_annee_more_90_percent
            plt.plot(data_annee_more_90_percent.share.tolist(), 'ro', color = '#48D1CC')
            labels = data_annee_more_90_percent.next_grade_corrected.values
            ax.set_xticks(np.arange(len(labels)))
            (markerline, stemlines, baseline) = ax.stem(
                    data_annee_more_90_percent.share,
                    color = '#48D1CC'
                    )
            plt.setp(baseline, visible=False)
            ax.xaxis.set_ticklabels(data_annee_more_90_percent.next_grade_corrected.values)
            fig.suptitle("{}, {}, N prochains grades = {}, plafond = {}".format(
                grade,
                annee,
                len(data_annee),
                part_max_des_agents_rep
                )
            )
            plt.savefig(os.path.join(
                project_path, 'ecrits\\descriptivestatisticsmultinomial\\Figures', '{}{}.pdf'
                ).format(grade, annee), format='pdf', dpi=1200)


# table with % people who stay in grade, % people who stay in corps, % people ailleurs (propo 10 biggest, n grade)
data_TTH1_2011 = data_long_w_echelon_IPP_corrected.query(
    "(annee == 2012) & (c_cir_2011 == 'TTH1') & (quarter == 1)"
    )
data_TTH1_2012 = data_TTH1_2011.c_cir.value_counts().reset_index().rename(columns={'index':'c_cir', 'c_cir':'count'})
data_TTH1_2012['share'] = data_TTH1_2012['count'] / data_TTH1_2012['count'].sum()
data_TTH1_2012['n_next_grade_hors_corps'] = len(data_TTH1_2012) - 2





# Look whether grade transitions within have same arrival IB
df_ib_exit = data_long_w_echelon_IPP_corrected_and_quarter_of_exit.query(
    '(annee == first_y_in_next_grade) & (quarter == first_quarter_exited)'
    )[['ident', 'ib']].rename(columns = {"ib":"ib_first_quarter_of_exit"})

data_long_w_echelon_IPP_corrected_and_quarter_of_exit = data_long_w_echelon_IPP_corrected_and_quarter_of_exit.merge(
    df_ib_exit, on = ['ident'], how = 'left'
    )

x = data_long_w_echelon_IPP_corrected_and_quarter_of_exit.query('(annee == 2011) & (quarter == 4)').groupby(
    ['c_cir_2011', 'next_grade']
    )['ib_first_quarter_of_exit'].value_counts(dropna = False).rename(
        columns = {"ib_first_quarter_of_exit":"ib_first_q_exit"}).reset_index().rename(
            columns = {0:'count_ib'}
            ).sort_values(['c_cir_2011', 'count_ib'], ascending = False)

plt.bar(x.query("(c_cir_2011 == 'TTH1') & (next_grade == 'TTH2')").copy()['ib_first_quarter_of_exit'].tolist(),
         x.query("(c_cir_2011 == 'TTH1') & (next_grade == 'TTH2')").copy()['count_ib'].tolist(),
         2
         )
plt.savefig(os.path.join(
                project_path, 'ecrits\\descriptivestatisticsmultinomial\\Figures', 'TTH1-TTH2-next_IB.png'), format='png'
                )

plt.bar(x.query("(c_cir_2011 == 'TTH2') & (next_grade == 'TTH3')").copy()['ib_first_quarter_of_exit'].tolist(),
         x.query("(c_cir_2011 == 'TTH2') & (next_grade == 'TTH3')").copy()['count_ib'].tolist(),
         2
         )
plt.savefig(os.path.join(
                project_path, 'ecrits\\descriptivestatisticsmultinomial\\Figures', 'TTH2-TTH3-next_IB.png'), format='png'
                )

plt.bar(x.query("(c_cir_2011 == 'TTH3') & (next_grade == 'TTH4')").copy()['ib_first_quarter_of_exit'].tolist(),
         x.query("(c_cir_2011 == 'TTH3') & (next_grade == 'TTH4')").copy()['count_ib'].tolist(),
         2
         )
plt.savefig(os.path.join(
                project_path, 'ecrits\\descriptivestatisticsmultinomial\\Figures', 'TTH3-TTH4-next_IB.png'), format='png'
                )

plt.bar(x.query("(c_cir_2011 == 'TTH4')").copy()['ib_first_quarter_of_exit'].tolist(),
        x.query("(c_cir_2011 == 'TTH4')").copy()['count_ib'].tolist(),
        2
        )
plt.savefig(os.path.join(
                project_path, 'ecrits\\descriptivestatisticsmultinomial\\Figures', 'TTH4-next_IB.png'), format='png'
                )


# Look whether grade transitions within corps have same echelon
df_echelon_exit = data_long_w_echelon_IPP_corrected_and_quarter_of_exit.query(
    '(annee == first_y_in_next_grade) & (quarter == first_quarter_exited)'
    )[['ident', 'echelon_IPP_modif_y_after_exit']].rename(
        columns = {"echelon_IPP_modif_y_after_exit":"echelon_first_quarter_of_exit"}
        )

data_long_w_echelon_IPP_corrected_and_quarter_of_exit = data_long_w_echelon_IPP_corrected_and_quarter_of_exit.merge(
    df_echelon_exit, on = ['ident'], how = 'left'
    )

x = data_long_w_echelon_IPP_corrected_and_quarter_of_exit.query('(annee == 2011) & (quarter == 4)').groupby(
    ['c_cir_2011', 'next_grade']
    )["echelon_first_quarter_of_exit"].value_counts(dropna = False).rename(
        columns = {"echelon_first_quarter_of_exit":"echelon_first_q_of_exit"}).reset_index().rename(
            columns = {0:'count_echelon'}
            ).sort_values(['c_cir_2011', 'count_echelon'], ascending = False)

plt.bar(x.query("(c_cir_2011 == 'TTH1') & (next_grade == 'TTH2')").copy()["echelon_first_quarter_of_exit"].tolist(),
         x.query("(c_cir_2011 == 'TTH1') & (next_grade == 'TTH2')").copy()['count_echelon'].tolist(),
         0.5
         )
plt.savefig(os.path.join(
                project_path, 'ecrits\\descriptivestatisticsmultinomial\\Figures', 'TTH1-TTH2-next_echelon.png'), format='png'
                )

plt.bar(x.query("(c_cir_2011 == 'TTH2') & (next_grade == 'TTH3')").copy()["echelon_first_quarter_of_exit"].tolist(),
         x.query("(c_cir_2011 == 'TTH2') & (next_grade == 'TTH3')").copy()['count_echelon'].tolist(),
         0.5
         )
plt.savefig(os.path.join(
                project_path, 'ecrits\\descriptivestatisticsmultinomial\\Figures', 'TTH2-TTH3-next_echelon.png'), format='png'
                )

plt.bar(x.query("(c_cir_2011 == 'TTH3') & (next_grade == 'TTH4')").copy()["echelon_first_quarter_of_exit"].replace(
    [55555], -2).tolist(), x.query("(c_cir_2011 == 'TTH3') & (next_grade == 'TTH4')").copy()['count_echelon'].tolist(), 0.5)
plt.savefig(os.path.join(
                project_path, 'ecrits\\descriptivestatisticsmultinomial\\Figures', 'TTH3-TTH4-next_echelon.png'), format='png'
                )

plt.bar(x.query("(c_cir_2011 == 'TTH4')").copy()["echelon_first_quarter_of_exit"].replace(
    [55555], -2).tolist(),
        x.query("(c_cir_2011 == 'TTH4')").copy()['count_echelon'].tolist(),
        0.5
        )
plt.savefig(os.path.join(
                project_path, 'ecrits\\descriptivestatisticsmultinomial\\Figures', 'TTH4-next_echelon.png'), format='png'
                )