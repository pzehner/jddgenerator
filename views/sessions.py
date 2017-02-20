#-*- coding: utf8 -*-


##
# imports
#


from __future__ import unicode_literals
import os
import logging
from jinja2 import Environment, FileSystemLoader
from ..utils import utils
from jdd import BasicView, TEMPLATE_DIRECTORY

SESSION_TEMPLATE = 'sessions.tex_template'
SESSION_PATTERN = 'session_{}.tex'
SESSIONS_CONTAINER_TEMPLATE = 'sessions_container.tex_template'
SESSIONS_CONTAINER_PATTERN = 'sessions_container.tex.sample'

class SessionsView(BasicView):
    """ Vue pour la génération d'un fichier LaTeX contenant les sessions

        La vue récupère les données stockées par les modèles et mises en ordre
        par le contrôleur. Elle utilise Jinja2 pour le moteur de template.

        Attributes:
            logger (:obj:`logging.Logger`): logger pour toute la classe.
            environment (:obj:`jinja2.environment.Environment`): enviornnement
                de templates pour Jinja2. Il a été adapté pour que la syntaxe
                coïncide avec LaTeX. Les accolades LaTeX faisaient interférence
                avec les accolades du langage de template par défaut.
    """
    logger = logging.getLogger('views.sessions.SessionsView')

    def retrieve_sessions(self, sessions):
        """ Formate les sessions dans le template

            Args:
                sessions (:obj:`list` of :obj:`Session`): liste des sessions
                    sous forme d'objets.

            Returns:
                :obj:`list` of :obj:`dict`: liste de dictionnaires contenant le
                nom de fichier à créer et le contenu texte.
        """
        # charger le template
        self.logger.debug("Charge le template \"{template}\"".format(
            template=os.path.join(
                TEMPLATE_DIRECTORY,
                SESSION_TEMPLATE
                )
            ))

        template = self.environment.get_template(SESSION_TEMPLATE)

        # mettre le contenu des sessions dans un template
        texts = []
        for session in sessions:
            session_dict = utils.todict(session)
            text = template.render(session_dict)
            file_name = SESSION_PATTERN.format(session.number)
            texts.append({
                'file_name': file_name,
                'text': text
                })

            self.logger.debug("Génére le texte pour la session \
\"{session}\"".format(session=session))

        return texts

    def retrieve_sessions_container(self, sessions_text, sessions_obj):
        """ Crée un conteneur de sessions à importer facilement

            Args:
                sessions_text (:obj:`list` of :obj:`dict`): liste de
                    dictionnaires des noms de fichiers LaTeX générés
                    pour chaque session et du contenu.
                sessions_obj (:obj:`list` of :obj:`Session`): liste des
                    sessions sous forme d'objets.

            Returns:
                :obj:`dict`: dictionnaire du nom de fichier et du texte
                de conteneur de sessions.
        """
        # charger le template
        self.logger.debug("Charge le template \"{template}\"".format(
            template=os.path.join(
                TEMPLATE_DIRECTORY,
                SESSIONS_CONTAINER_TEMPLATE
                )
            ))

        template = self.environment.get_template(SESSIONS_CONTAINER_TEMPLATE)

        # mettre les noms de fichiers dans le template
        sessions = {'sessions': [
            {
                'file_name': st['file_name'],
                'date': so.start,
                } for st, so in zip(sessions_text, sessions_obj)
            ]}

        text = template.render(sessions)
        self.logger.debug("Génére le texte pour le conteneur de sessions")
        file_name = SESSIONS_CONTAINER_PATTERN

        return {
                'file_name': file_name,
                'text': text
                }
