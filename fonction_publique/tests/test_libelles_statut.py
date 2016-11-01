from __future__ import division


from fonction_publique.base import get_careers
decennie = 1950
debug = False
libemploi = get_careers(variable = 'libemploi', decennie = decennie, debug = debug, where = "annee >= 2000")
print libemploi.annee.value_counts()
statut = get_careers(variable = 'statut', decennie = decennie, debug = debug, where = "annee >= 2000")
print statut.annee.value_counts()
print statut.statut.value_counts()
libemploi = (libemploi.merge(
    statut.query("statut in ['T', 'H']"),
    how = 'inner',
    ))
libemploi_annee = libemploi.query('annee == 2000')
for statut_i in libemploi_annee.statut.unique():
    print statut_i
    print libemploi_annee.query('statut == @statut_i').libemploi.value_counts()