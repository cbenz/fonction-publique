# -*- coding: utf-8 -*-


from datetime import datetime

import openfisca_france
from openfisca_france.model.base import CAT


TaxBenefitSystem = openfisca_france.init_country()
tax_benefit_system = TaxBenefitSystem()


scenario_arguments = dict(
    period = 2015,
    parent1 = dict(
        date_naissance = datetime.date(1972, 1, 1),
        categorie_salarie = CAT['public_titulaire_hospitaliere'],  # 'public_titulaire_territoriale',
        ),
    menage = dict(
        zone_apl = 1,
        ),
    )

scenario = tax_benefit_system.new_scenario()
scenario.init_single_entity(**scenario_arguments)
simulation = scenario.new_simulation(debug = False)
