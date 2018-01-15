#-*- coding: utf8 -*-
"""Utilisation de JDD Generator en tant que module

Ceci est un exemple d'utilisation du projet comme module. Les paramètres passés
aux méthodes ont les valeurs par défaut, mais sont laissés pour la pédagogie.

"""


# gérer nativement les strings en unicode
from __future__ import unicode_literals

# utiliser un mécanisme plus avancé d'import
from __future__ import absolute_import

# gérer les logs
import logging
logging.basicConfig(level=logging.INFO)

# imorter l'outil de configuration du projet
from jdd_generator.config import set_config

# importer les contrôleurs du projet
from jdd_generator.controllers.planning import PlanningController
from jdd_generator.controllers.booklet import BookletController
from jdd_generator.controllers.jdd import JddController


if __name__ == '__main__':
    # charger la configuration depuis le fichier par défaut
    set_config()

    # dossier de sortie
    output_directory = 'jdd'

    # planning
    planning = PlanningController()
    planning.create(
            students_file='listing.ini',
            repartitions_file='timings.ini',
            planning_file='planning.ini'
            )

    planning.retrieve(directory=output_directory)

    # recueil
    booklet = BookletController()
    booklet.create(
            students_file='listing.ini',
            repartitions_file='timings.ini',
            booklet_file='booklet.ini',
            abstracts_file='abstracts.ini',
            directory_pictures='photos'
            )

    booklet.retrieve(directory=output_directory)

    # fichier principal
    jdd = JddController()
    jdd.retrieve(directory=output_directory)
