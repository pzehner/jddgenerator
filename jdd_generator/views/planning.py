#-*- coding: utf8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import
import os
import logging
from ..utils import utils
from .jdd import BasicView, TEMPLATE_DIRECTORY


SESSION_TEMPLATE = 'session.tex_template'
SESSION_PATTERN = 'session_{}.tex'
PLANNING_TEMPLATE = 'planning.tex_template'
PLANNING_PATTERN = 'planning.tex.sample'


class PlanningView(BasicView):
    """Vue pour la génération d'un fichier LaTeX contenant le planning.

    La vue récupère les données stockées par les modèles et mises en ordre par
    le contrôleur. Elle utilise Jinja2 pour le moteur de template.

    Le planning se divise en un fichier principal `PLANNING` et une série de
    fichiers pour chaque session `SESSION`. Ceci évite d'avoir un seul fichier
    de planning qui serait très gros et pas pratique pour les modifications à la
    dernière minute. Néanmoins, utiliser cette structure complexifie pas mal le
    code, parce qu'il faut générer plusieurs fichiers.

    Attributes:
        logger (:obj:`logging.Logger`): logger pour toute la classe.
        environment (:obj:`jinja2.environment.Environment`): enviornnement de
            templates pour Jinja2. Il a été adapté pour que la syntaxe coïncide
            avec LaTeX. Les accolades LaTeX faisaient interférence avec les
            accolades du langage de template par défaut.
        session_template_loaded (bool): flag pour indiquer si le template de
            session a été chargé par Jinja2.
        planning_template_loaded (bool): flag pour indiquer si le template de
            planning a été chargé par Jinja2.
    """
    logger = logging.getLogger('views.sessions.SessionsView')

    def __init__(self):
        self.session_template_loaded = False
        self.planning_template_loaded = False

    def retrieve(self, events):
        """Formate les évents du planning dans le template.

        Args:
            events (:obj:`list` of :obj:`Event`): liste des évents.

        Returns:
            :obj:`list` of :obj:`dict`: liste de dictionnaires contenant le nom
            des fichiers et leur contenu pour le planning.

        """
        # la liste des fichiers à écrire, c'est-à-dire le fichier de planning et
        # les fichiers de session
        files_content = []

        # Jinja2 n'accepte que des dictionnaires en entrée, on va devoir tout
        # convertir
        events_dict = []

        # parcourir chaque event
        for event in events:
            # convertir en dictionnaire
            event_dict = utils.todict(event)
            events_dict.append(event_dict)

            # sessions
            # Il y a un traitement supplémentaire pour les session. Comme on
            # veut les rendre chacune dans un fichier, il faut les traiter à
            # part.
            if event.event_type == 'session':
                session = self._retrieve_session(event_dict)
                event_dict['file_name'] = session['file_name']
                event_dict['event_type'] = 'session'

                files_content.append(session)

        # rendre le fichier de planning
        files_content.append(self._retrieve_planning(events_dict))

        return files_content

    def _retrieve_session(self, session_dict):
        """Formate une sessions dans le template.

        Args:
            session_dict (:obj:`dict`): session sous forme de dictionnaire.

        Returns:
            :obj:`dict`: dictionnaire contenant le nom de fichier à créer et le
            contenu texte.

        """
        # charger le template
        if not self.session_template_loaded:
            self.logger.debug("Charge le template \"{template}\"".format(
                template=os.path.join(
                    TEMPLATE_DIRECTORY,
                    SESSION_TEMPLATE
                    )
                ))

        template = self.environment.get_template(SESSION_TEMPLATE)
        self.session_template_loaded = True

        # mettre le contenu des sessions dans un template
        text = template.render(session_dict)
        file_name = SESSION_PATTERN.format(session_dict['number'])

        self.logger.debug("Génére le texte pour la session \
\"{session}\"".format(session=session_dict['number']))

        return {
            'file_name': file_name,
            'text': text
            }

    def _retrieve_planning(self, events_dict):
        """Formate le fichier principal du planning.

        Args:
            events_dict (:obj:`list` of :obj:`dict`): liste des évents sous
                forme de dictionnaire.

        Returns:
            :obj:`dict`: dictionnaire du nom de fichier et du texte du fichier
            principal du planning.

        """
        # charger le template
        if not self.planning_template_loaded:
            self.logger.debug("Charge le template \"{template}\"".format(
                template=os.path.join(
                    TEMPLATE_DIRECTORY,
                    PLANNING_TEMPLATE
                    )
                ))

        template = self.environment.get_template(PLANNING_TEMPLATE)
        self.planning_template_loaded = True

        # rendre le planning
        text = template.render({'events': events_dict})
        file_name = PLANNING_PATTERN
        self.logger.debug("Génére le texte pour le planning")

        return {
                'file_name': file_name,
                'text': text
                }
