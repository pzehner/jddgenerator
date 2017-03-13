#-*- coding: utf8 -*-
"""Utilisation de JDD Generator en tant que module

Ceci est un exemple d'utilisation du projet comme module.

"""


from __future__ import unicode_literals
from __future__ import absolute_import
import logging
from jdd_generator.controllers.planning import PlanningController
from jdd_generator.controllers.booklet import BookletController
from jdd_generator.controllers.jdd import JddController


logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
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
