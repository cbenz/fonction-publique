# -*- coding:utf-8 -*-


from __future__ import division


from slugify import slugify
import logging

from fonction_publique.sandbox.grade_matching import load_libelles_emploi_data


log = logging.getLogger(__name__)


def test_slugify():
    libemplois = load_libelles_emploi_data(decennie = 1970, debug = True, force_recreate = True)

    libemplois.name = 'values'
    mylibemplois = libemplois.reset_index()
    slugified = mylibemplois.libemploi.apply(slugify, separator = "_")
    slugified = mylibemplois.libemploi.apply(slugify, separator = "_")
    slugified.unique()

    mylibemplois.libemploi[:100]


if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    test_slugify()

