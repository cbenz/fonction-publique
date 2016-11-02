# -*- coding:utf-8 -*-


from __future__ import division


from slugify import slugify


from fonction_publique.sandbox.grade_matching import load_libelles_emploi_data


def test_slugify():
    libemplois = load_libelles_emploi_data(decennie = 1970, debug = True, force_recreate = True)

    libemplois.name = 'values'
    mylibemplois = libemplois.reset_index()
    print len(mylibemplois.libemploi)
    slugified = mylibemplois.libemploi.apply(slugify, separator = "_")
    slugified = mylibemplois.libemploi.apply(slugify, separator = "_")
    print len(slugified.unique())
    slugified.unique()

    mylibemplois.libemploi[:100]

if __name__ == '__main__':
    # logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    test_slugify()

