#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" -- a versatile microsimulation free software"""


from setuptools import setup, find_packages


setup(
    name = 'Fonction-Publique',
    version = '0.1',
    author = 'OpenFisca Team',
    author_email = 'contact@openfisca.fr',
    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Information Analysis",
        ],
    description = u'',
    keywords = 'benefit france microsimulation social tax',
    license = 'http://www.fsf.org/licensing/licenses/agpl-3.0.html',
    url = 'https://github.com/openfisca/openfisca-france',

    data_files = [
        ('share/openfisca/openfisca-france', ['LICENSE', 'README.md']),
        ],

    include_package_data = True,  # Will read MANIFEST.in
    install_requires = [
        'numpy >= 1.6',
        'OpenFisca-France >= 0.5.3',
        ],

    packages = find_packages(exclude=['fonction_publique.tests*']),
    test_suite = 'nose.collector',
    )
