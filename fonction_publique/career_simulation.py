from __future__ import division


from openfisca_core import periods
import os
import pandas as pd
import pkg_resources
import datetime

from time import gmtime, strftime

asset_path = os.path.join(
    pkg_resources.get_distribution('openfisca_france').location,
    'openfisca_france',
    'assets',
    'grilles_fonction_publique',
    )

grille_adjoint_technique = os.path.join(
    asset_path,
    'FPT_adjoint_technique.xlsx',
    )

grille_adjoint_technique = pd.read_excel(grille_adjoint_technique, encoding='utf-8')
dates_effet_grille = grille_adjoint_technique['date_effet_grille']


donnees_adjoints_techniques = os.path.join(
    asset_path,
    'donnees_indiv_adjoint_technique_test.xlsx',
    )

donnees_adjoints_techniques = pd.read_excel(donnees_adjoints_techniques)


datefunc = lambda x: datetime.strptime(x, '%Y-%m-%d')


def timestampToDate(timestamp, datePattern):
    return strftime("%b %d %Y %H:%M", gmtime(float(timestamp)))


def days_between(m1, m2):
    m1 = datetime.strptime(m1, "%Y-%m")
    m2 = datetime.strptime(m2, "%Y-%m-%d")
    return ((m2 - m1).days)


class AgentFpt:
    'common base class for all agent of French fonction publique'
    agentfptCount = 0
    _registry = []

    def __init__(self, identif, period, grade, echelon):
        self.identif = identif
        self.period = period
        self.grade = grade
        self.echelon = echelon
        self._registry.append(self)
        AgentFpt.agentfptCount += 1
#
#  def displayCount(self):
#        return AgentFpt.agentfptCount

    def display_agent(self):
        print "Identif : ", self.identif, "Period :", self.period, ", Grade :", self.grade, ", Echelon :", self.echelon

    def echelon_max(self):
        period = periods.period(self.period)
        indiv_grille = grille_adjoint_technique[
            (grille_adjoint_technique['code_grade_NEG'] == self.grade) &
            (grille_adjoint_technique['date_effet_grille'] < str(period.start))
            ]

        indiv_grille = indiv_grille[
            (grille_adjoint_technique['date_effet_grille'] == indiv_grille['date_effet_grille'].max())
            ]
        echelon_max = indiv_grille['echelon'].max()
        return echelon_max

    def grille_date_effet_at_start(self):
        period = periods.period(self.period)
        indiv_grille = grille_adjoint_technique[
            (grille_adjoint_technique['code_grade_NEG'] == self.grade) &
            (grille_adjoint_technique['date_effet_grille'] < str(period.start))
            ]
        indiv_grille = indiv_grille[
            (grille_adjoint_technique['date_effet_grille'] == indiv_grille['date_effet_grille'].max())
            ]
        date_debut_effet = indiv_grille['date_effet_grille'].map(lambda x: x.strftime('%Y-%m'))
        date_debut_effet = periods.period(date_debut_effet.unique()[0])
        return date_debut_effet.start

    def next_grille_date_effet(self):  # grade level
        grille_date_effet_at_start = self.grille_date_effet_at_start()
        next_grille_date_effet = grille_adjoint_technique[
            (grille_adjoint_technique['code_grade_NEG'] == self.grade) &
            (grille_adjoint_technique['date_effet_grille'] > str(grille_date_effet_at_start))
            ]
        next_grille_date_effet = next_grille_date_effet[
            (grille_adjoint_technique['date_effet_grille'] == next_grille_date_effet['date_effet_grille'].min())
            ]
        if next_grille_date_effet.shape == (0, 12):
            date_debut_effet = self.grille_date_effet_at_start()
        else:
            date_debut_effet = next_grille_date_effet['date_effet_grille'].map(lambda x: x.strftime('%Y-%m'))
            date_debut_effet = periods.period(date_debut_effet.unique()[0])
            date_debut_effet = date_debut_effet.start
        return date_debut_effet

    def echelon_period_for_grille_at_start(self, speed):
        period = periods.period(self.period)
        indiv_grille = grille_adjoint_technique[
            (grille_adjoint_technique['code_grade_NEG'] == self.grade) &
            (grille_adjoint_technique['echelon'] == self.echelon) &
            (grille_adjoint_technique['date_effet_grille'] < str(period.start))
            ]
        indiv_grille = indiv_grille[
            (grille_adjoint_technique['date_effet_grille'] == indiv_grille['date_effet_grille'].max())
        ]
        if speed:
            period_at_echelon = indiv_grille['min_mois'].squeeze()
        else:
            period_at_echelon = indiv_grille['max_mois'].squeeze()

        echelon_period_at_start = periods.period((u'month'), periods.instant(period), int(period_at_echelon))
        return echelon_period_at_start

    def next_change_of_legis_grille(self, speed):  # echelon level
        period = periods.period(self.period)
        grille_date_effet_at_start = self.grille_date_effet_at_start()
        echelon_period_at_start = self.echelon_period_for_grille_at_start(speed)
        next_change_of_legis_grille = grille_adjoint_technique[
            (grille_adjoint_technique['code_grade_NEG'] == self.grade) &
            (grille_adjoint_technique['echelon'] == self.echelon) &
            (grille_adjoint_technique['date_effet_grille'] > str(period.start))
            ]
        if speed:
            condition = (
                next_change_of_legis_grille['min_mois'] !=
                [echelon_period_at_start.size] * len(next_change_of_legis_grille['min_mois'])
                )
            next_change_of_legis_grille = next_change_of_legis_grille[condition]
            next_change_of_legis_grille = next_change_of_legis_grille[next_change_of_legis_grille['date_effet_grille'] == next_change_of_legis_grille['date_effet_grille'].min()]
            if next_change_of_legis_grille.empty is True:
                next_change_of_legis_grille = grille_date_effet_at_start
            else:
                next_change_of_legis_grille = next_change_of_legis_grille['date_effet_grille'].map(lambda x: x.strftime('%Y-%m'))
                next_change_of_legis_grille = periods.period(next_change_of_legis_grille.unique()[0])
                next_change_of_legis_grille = next_change_of_legis_grille.start
        else:
            next_change_of_legis_grille = next_change_of_legis_grille[next_change_of_legis_grille['max_mois'] != [echelon_period_at_start.size] * len(next_change_of_legis_grille['max_mois'])]
            next_change_of_legis_grille = next_change_of_legis_grille[next_change_of_legis_grille['date_effet_grille'] == next_change_of_legis_grille['date_effet_grille'].min()]

            if next_change_of_legis_grille.empty is True:
                next_change_of_legis_grille = grille_date_effet_at_start
            else:
                next_change_of_legis_grille = next_change_of_legis_grille['date_effet_grille'].map(lambda x: x.strftime('%Y-%m'))
                next_change_of_legis_grille  = periods.period(next_change_of_legis_grille.unique()[0])
                next_change_of_legis_grille  = next_change_of_legis_grille.start

        return next_change_of_legis_grille

    def end_echelon_grille_in_effect_at_start(self, speed):
        return self.echelon_period_for_grille_at_start(speed).stop

    def echelon_period_with_grille_in_effect_at_end(self, speed):
        instant = self.end_echelon_grille_in_effect_at_start(speed)
        indiv_grille = grille_adjoint_technique[
            (grille_adjoint_technique['code_grade_NEG'] == self.grade) &
            (grille_adjoint_technique['echelon'] == self.echelon) &
            (grille_adjoint_technique['date_effet_grille'] < str(instant))
            ]
        indiv_grille = indiv_grille[
            (grille_adjoint_technique['date_effet_grille'] == indiv_grille['date_effet_grille'].max())
        ]
        if speed:
            period_at_echelon = indiv_grille['min_mois'].squeeze()
        else:
            period_at_echelon = indiv_grille['max_mois'].squeeze()
        echelon_period_at_end = periods.period((u'month'), instant, int(period_at_echelon))
        return echelon_period_at_end

    def change_of_grille_during_period(self, speed):
        period_at_start = self.echelon_period_for_grille_at_start(speed)
        period_at_end = self.echelon_period_with_grille_in_effect_at_end(speed)
        return period_at_start != period_at_end

    def echelon_period_with_grille_in_effect(self, speed):
        echelon_max = self.echelon_max()
        next_echelon = self.echelon + 1
        diff_change_legis_date_entree_echelon = days_between(str(self.period), str(self.next_change_of_legis_grille(speed)))
        period_echelon_days = (self.echelon_period_for_grille_at_start(speed)).days
        if next_echelon <= echelon_max:
            if self.change_of_grille_during_period(speed):
                if diff_change_legis_date_entree_echelon < period_echelon_days and self.next_change_of_legis_grille(speed) > self.grille_date_effet_at_start() and diff_change_legis_date_entree_echelon > self.echelon_period_with_grille_in_effect_at_end(speed).days:
                    echelon_period = diff_change_legis_date_entree_echelon
                    echelon_period = periods.instant(self.period).period('month', round(echelon_period / 30))
                else:
                    echelon_period = self.echelon_period_with_grille_in_effect_at_end(speed)
            else:
                echelon_period = self.echelon_period_for_grille_at_start(speed)
        else:
            echelon_period = periods.period(self.period)
        return echelon_period.size

    def date_change_career_state(self, speed):
        period_to_offset = (self.echelon_period_with_grille_in_effect(speed))
        date_change = periods.period('month', self.period).offset(period_to_offset)
        return date_change

    def get_career_states_in_grade(self, speed):
        career_states = [self.period]
        echelon = []
        grade = []
        identif = []
#        grille_in_effect = []
        if self.echelon == self.echelon_max():
                echelon.append(self.echelon)
                grade.append(self.grade)
                identif.append(self.identif)
                result = [identif, grade, echelon, career_states]
                result = pd.DataFrame(result).transpose()[:]
                return result
        else:
            while self.echelon < self.echelon_max():
                    career_state = self.date_change_career_state(speed)
                    career_state = periods.period(career_state)
                    career_states.append(career_state)
                    echelon.append(self.echelon)
                    grade.append(self.grade)
                    identif.append(self.identif)
                    setattr(self, 'period', career_state)
                    setattr(self, 'echelon', self.echelon + 1)
            if self.echelon == self.echelon_max():
                    career_state = career_state
                    career_states.append(career_state)
                    echelon.append(self.echelon)
                    grade.append(self.grade)
                    identif.append(self.identif)
        career_states_formatted = map(periods.instant, career_states)
        result = [identif, grade, echelon, career_states_formatted]
        result = pd.DataFrame(result).transpose()[:-1]
        result.columns = ("id", "code_grade_NEG", "echelon", "date_du_changement")
        return result


#agents_fpt_identif = [agent1.identif, agent2.identif, agent5.identif]
#agents_fpt_echelon = [agent1.echelon, agent2.echelon, agent5.echelon]
#agents_fpt_grade = [agent1.grade, agent2.grade, agent5.grade]
#agents_fpt_period = [agent1.period, agent2.period, agent5.period]

#_registry = []
#all_agents_fpt = []
#careers = pd.DataFrame()
#identif = []
#changement_grille = pd.DataFrame()


#def get_careers(agents):
#    set_id, set_grade, set_echelon, set_period = set(), set(), set(), set()
#    career_state = pd.DataFrame()
#    career_state_loop = pd.DataFrame(index=range(0,4),columns=[''], dtype='float')
#    for agent in agents:
#        if isinstance(agent, AgentFpt):
#           set_id.add(agent.identif)
#           set_grade.add(agent.grade)
#           set_echelon.add(agent.echelon)
#           set_period.add(agent.period)
#
#    for grade in set_grade:
#        for echelon in set_echelon:
#           for period in set_period:
#                condition = (
#                   (agent.grade == grade) &
#                   (agent.echelon == echelon) &
#                   (agent.period == period)
#                   )
#                career_state = AgentFpt.get_career_states_in_grade(
#                    agent,
#                    True
#                    )
#                career_state_loop = np.where(condition, career_state, career_state_loop)
#                career_state_loop = pd.DataFrame(career_state)
#                career_state = career_state.append(career_state_loop)
#                return career_state


#  def grille_in_effect(self, speed):

#  def get_career_states_in_grade_without_law_change(self, speed):
#        career_states = [self.period]
#        echelon = []
#        grade = []
#        identif = []
#        period_in_echelon = []
##        grille_in_effect = []
#        while self.echelon <= self.echelon_max():
#            if periods.instant(self.date_change_career_state(speed)) > periods.instant(self.next_grille_date_effet()):
#                if periods.instant(self.period) > periods.instant(2015):
#                    period_to_offset = (self.echelon_period_with_grille_in_effect(speed)).size
#                    career_state = self.date_change_career_state(speed)
#                    career_state = periods.period(career_state)
#                    career_states.append(career_state)
#                    echelon.append(self.echelon)
#                    grade.append(self.grade)
#                    identif.append(self.identif)
#                    period_in_echelon.append(period_to_offset)
#                    setattr(self, 'period', career_state)
#                    setattr(self, 'echelon', self.echelon + 1)
#                else:
#                    period_to_offset = (self.echelon_period_with_grille_in_effect(speed)).size
#                    period_in_echelon.append(period_to_offset)
#                    career_state = self.date_change_career_state(speed)
#                    career_state = periods.period(career_state)
#                    career_states.append(career_state)
#                    echelon.append(self.echelon)
#                    grade.append(self.grade)
#                    identif.append(self.identif)
#                    break
#            else:
#                period_to_offset = (self.echelon_period_with_grille_in_effect(speed)).size
#                period_in_echelon.append(period_to_offset)
#                career_state = self.date_change_career_state(speed)
#                career_state = periods.period(career_state)
#                career_states.append(career_state)
#                echelon.append(self.echelon)
#                grade.append(self.grade)
#                identif.append(self.identif)
#                setattr(self, 'period', career_state)
#                setattr(self, 'echelon', self.echelon + 1)
#
#        result = [identif, grade, echelon, career_states, period_in_echelon]
#        result = pd.DataFrame(result).transpose()[:-1]
#        return result



#
#if __name__ == '__main__':
#    agents = [agent1, agent2, agent3, agent4, agent5, agent6]
#    x = get_careers(agents)
#
