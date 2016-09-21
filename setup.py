#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" -- simulating French public servants' careers"""


from setuptools import setup, find_packages


setup(
    name = 'Fonction-Publique',
    version = '0.1',
    author = 'IPP Team',
    author_email = 'lisa.degalle@gmail.com',
    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Information Analysis",
        ],
    description = u'',
    keywords = 'public servant france microsimulation career earnings',
    license = 'http://www.fsf.org/licensing/licenses/agpl-3.0.html',
    url = 'https://git.framasoft.org/ipp/fonction-publique',

    data_files = [
        ('share/openfisca/fonction-publique', ['LICENSE', 'README.md']),
        ],

    include_package_data = True,  # Will read MANIFEST.in
    install_requires = [
        'numpy >= 1.6',
        #  'OpenFisca-France >= 0.5.3',
        'pandas >= 0.18.1',
        ],

    packages = find_packages(exclude=['fonction_publique.tests*']),
    test_suite = 'nose.collector',
    )
