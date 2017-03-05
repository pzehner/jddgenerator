# -*- coding: utf8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import
import os
import logging
from codecs import open
from jinja2 import Environment, FileSystemLoader
from ..utils import utils


TEMPLATE_DIRECTORY = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'templates'
        )


MAIN_TEMPLATE = 'jdd.tex'
MAIN_PATTERN = 'jdd.tex'


class JddView(object):
    """Vue pour la génération des conteneurs des différents documents des JDD.

    La vue crée les fichier LaTeX conteneurs qui importent les autres fichiers
    LaTeX générés.

    Attributes:
        logger (:obj:`logging.Logger`): logger pour toute la classe.

    """
    logger = logging.getLogger('views.sessions.JddView')

    def retrieve(self):
        """Copie les fichiers conteneurs.

        Returns:
            :obj:`dict`: dictionnaire du nom de fichier et du texte.

        """
        # charger les fichiers
        main_path = os.path.join(TEMPLATE_DIRECTORY, MAIN_TEMPLATE)
        with open(main_path, 'r', encoding='utf8') as file:
            self.logger.debug("Charge le conteneur principal \
\"{path}\"".format(path=main_path))

            main = file.read()

        return {
                'file_name': MAIN_PATTERN,
                'text': main,
                }

class BasicView(object):
    """Vue basique.

    La vue récupère les données stockées par les modèles et mises en ordre par
    le contrôleur. Elle utilise Jinja2 pour le moteur de template.

    Cette vue sert de modèle aux autres vues, elle se contente de mettre en
    place l'environnement pour Jinja2.

    Attributes:
        environment (:obj:`jinja2.environment.Environment`): enviornnement de
            templates pour Jinja2. Il a été adapté pour que la syntaxe coïncide
            avec LaTeX. Les accolades LaTeX faisaient interférence avec les
            accolades du langage de template par défaut.

    """
    environment = Environment(
            loader=FileSystemLoader(TEMPLATE_DIRECTORY),
            block_start_string=r'\block{',
            block_end_string=r'}',
            variable_start_string=r'\var{',
            variable_end_string=r'}',
            comment_start_string=r'\#{',
            comment_end_string=r'}',
            line_statement_prefix=r'%%',
            line_comment_prefix=r'%#',
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
            )

    environment.filters['time'] = utils.format_time
    environment.filters['date'] = utils.format_date
    environment.filters['color'] = utils.format_color
    environment.filters['printable'] = utils.format_printable
