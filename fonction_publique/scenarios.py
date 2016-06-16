# -*- coding: utf-8 -*-


import datetime

import openfisca_france
from openfisca_france.model.base import CAT

from fonction_publique.career_simulation import AgentFpt

TaxBenefitSystem = openfisca_france.init_country()
tax_benefit_system = TaxBenefitSystem()


agent1 = AgentFpt(1, '2006-12', 793, 1)
agent1_career = agent1.get_career_states_in_grade(True)


corps = 'adjoint_technique'

grade = dict(
    (str(period)[:-3], grade)
    for period, grade in zip(
        agent1_career.date_du_changement,
        agent1_career.code_grade_NEG,
        )
    )

echelon = dict(
    (str(period)[:-3], echelon)
    for period, echelon in zip(
        agent1_career.date_du_changement,
        agent1_career.echelon,
        )
    )

scenario_arguments = dict(
    period = '2006-01',
    parent1 = dict(
        date_naissance = datetime.date(1972, 1, 1),
        categorie_salarie = CAT['public_titulaire_territoriale'],  # 'public_titulaire_hospitaliere',
        corps = corps,
        grade = grade,
        echelon = echelon,
        ),
    )

scenario = tax_benefit_system.new_scenario()

scenario.init_single_entity(**scenario_arguments)


simulation = scenario.new_simulation(debug = False)

print simulation.calculate('grade', period = '2006-12')
print simulation.calculate('grade', period = '2007-01')

print simulation.calculate('echelon', period = '2006-12')
print simulation.calculate('echelon', period = '2007-01')