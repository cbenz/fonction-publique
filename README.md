# Fonction publique

Modelling French public servants' careers.

## Install

````shell
git clone https://framagit.org/ipp/fonction-publique
cd fonction-publique
pip install -e .
````

## Requirements

To be able to use this package you need access to CNRACL career data and salary scale data.


## Configuration

You need to configure some important paths through the file `config.ini` located in in the user configuration directory for `fonction-publique`.
You can retrieve this location by running the following test:
````shell
nosetests fonction_publique/tests/test_config.py -svx
````


## Clean the raw data

Raw data needs to be cleaned to be used by the various programs.
This takes a long time and can be achieved by executing the following command
````shell
clean_career -v
````

## Extract the relevant information from the clean data and filter it to keep only what is needed for the estimation
````shell
generate_data -v
````


  




