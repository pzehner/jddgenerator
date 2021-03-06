#-*- coding: utf8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

import os
import sys
import logging
from datetime import timedelta, datetime
from codecs import open

from ConfigParser import SafeConfigParser
from colour import Color

from .jdd import BasicController, OUTPUT_DIRECTORY
from ..utils import utils
from ..utils.csv_dict import CSVDict
from ..models.planning import Event, Session, Presentation
from ..models.jdd import Student, PhD, Supervizor, Director
from ..views.planning import PlanningView
from ..config import config


STUDENTS_FILE = 'listing.ini'
REPARTITIONS_FILE = 'timings.ini'
PLANNING_FILE = 'planning.ini'
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = DATE_FORMAT + ' ' + TIME_FORMAT


class PlanningController(BasicController):
    """Contrôleur pour la génération des fichiers de planning.

    Le contrôleur donne accès aux méthodes pour la génération des fichiers de
    planning. La méthode `create` récupère les données des fichiers d'entrée,
    puis les ordonne avec les classes des modèles. La méthode `retrieve` envoit
    ces données à la vue pour les formatter en fichiers LaTeX. Le résultat est
    ensuite écrit sur le disque.

    Attributes:
        logger (:obj:`logging.Logger`): logger pour toute la classe.
        presentations (:obj:`list` of :obj:`Presentation`): liste des
            présentations (n'a pas vraiment de sens en tant qu'attribut, mais ça
            permet de faciliter le passage de cette variable).
        events (:obj:`list` of :obj:`Event`): liste des évents.

    """
    logger = logging.getLogger('controllers.planning.PlanningController')

    def __init__(self):
        self.presentations = []
        self.events = []

    def create(self, planning_file=PLANNING_FILE, students_file=STUDENTS_FILE,
            repartitions_file=REPARTITIONS_FILE):

        """Crée la structure de donnée depuis les différents fichiers d'entrée.

        Args:
            planning_file (unicode): fichier de configuration des événements qui
                contient pour chaque évent leur jour, heure, chairman et couleur
                d'affichage sur le programme.
            students_file (unicode): fichier de configuration pour charger le
                listing CVS des doctorants, qui doit contenir les sujets, les
                doctorants et les encadrants.
            repartitions_file (unicode): fichier de configuration pour charger
                le listing CVS des timings, qui contient l'affectation de chaque
                présentation dans les sessions.

        """
        # créer les évents
        self._create_events(planning_file)

        # créer les présentations
        self._create_presentations(students_file)

        # créer les timings
        self._apply_repartitions(repartitions_file)

        # ordonner les évents
        self._sort_events()

        # assigner les présentations dans l'ordre aux sessions
        self._sort_presentations()

    def retrieve(self, directory=OUTPUT_DIRECTORY):
        """Donne une représentation du planning en passant par la vue.

        Appelle la vue pour convertir les données en LaTeX, puis écris le
        résultat sur le disque et crée l'arborescence.

        Args:
            directory (unicode): dossier de sortie où enregistrer les fichiers.

        """
        # on crée une vue et lui passe les données
        view = PlanningView()
        files_content = view.retrieve(self.events)

        # dossier pour écrire les fichiers de planning
        directory_planning = os.path.join(directory, 'planning')

        # écrire
        self._write(files_content, directory_planning)

    def _create_events(self, planning_file):
        """Extraire les données du planning.

        Args:
            planning_file (unicode): chemin vers le fichier de configuration
                pour charger la liste CSV des entrées du planning. À son niveau,
                les sessions, les pauses ou les discours sont des évents. Dans
                le contrôleur, les sessions sont traitées à part (parce qu'elles
                contiennent des présentations, qui elles-mêmes contiennent
                d'autres éléments, ce nécessite un traitement séparé).

        """
        # lire le fichier CSV
        planning = CSVDict()
        planning.read(planning_file)

        # créer les objets
        self.events = []

        # parcourir tous les évents du planning
        for event in planning:
            # extraction de certains paramètres en avance
            # jour de l'évent
            # On doit convertir les `/` en `-` parce que Libre Office Calc est
            # un connard qui respecte pas le standard ISO 8601 tout en te
            # faisant croire qu'il le respecte. Il l'encode avec des `/` au lieu
            # de `-`.
            day_str = event['day'].replace('/', '-')
            day = datetime.strptime(
                    day_str,
                    DATE_FORMAT
                    )

            # début de l'évent
            # On recrée une date complète jour + heure et pas seulement l'heure,
            # c'est plus facile à manipuler avec le module `datetime`.
            start_str = event['start']
            start = datetime.strptime(
                    day_str + ' ' + start_str,
                    DATETIME_FORMAT
                    )

            # fin de l'évent
            # même astuce que pour le début de l'évent
            stop_str = event['stop']
            stop = datetime.strptime(
                    day_str + ' ' + stop_str,
                    DATETIME_FORMAT
                    )

            # couleur du bandeau de l'évent
            # Le module colour permet plusieurs représentations de la couleur,
            # on permet ici que chaque mode soit accepté.
            color_mode = event['color-mode']
            color_value = event['color']
            if color_value.startswith('#'):
                color = Color(color_value)

            else:
                color_dict = {color_mode: utils.read_tuple(color_value)}
                color = Color(**color_dict)

            # selon le type de l'évent, on crée l'objet adéquat
            # bon, on cherche surtout à repérer les sessions
            event_type = event['type'].lower()
            if event_type == 'session':
                event_object = Session(
                        number=int(event['number']),
                        color=color,
                        day=day,
                        start=start,
                        stop=stop,
                        chairman=event['chairman']
                        )

            else:
                number = event['number']
                event_object = Event(
                        name=event['type'].title(),
                        number=int(number) if number else 0,
                        color=color,
                        day=day,
                        start=start,
                        stop=stop,
                        chairman=event['chairman']
                        )

            # on sauvegarde l'objet
            self.events.append(event_object)
            self.logger.debug("Ajoute l'évent \"{event}\" au planning".format(
                event=event_object
                ))

    def _create_presentations(self, students_file):
        """Extraire les données de présentations.

        Args:
            students_file (unicode): fichier de configuration pour charger la
                liste CSV des doctorants, qui doit contenir les sujets, les
                doctorants et les encadrants.
        """
        # initialiser les présentations
        self.presentations = []

        # obtenir la liste des thèses depuis le fichier de listing des
        # doctorants
        phds = self._get_phds(students_file)

        # on crée les présentations depuis la liste des thèses
        for code, come_flag, phd in phds:
            # si le doctorant n'assiste pas aux JDD, on ne l'ajoute pas au
            # planning
            if not come_flag:
                continue

            # créer la présentation depuis le code et attacher la thèse
            presentation = Presentation(
                    code=code
                    )

            presentation.set_phd(phd)

            # sauver
            self.presentations.append(presentation)
            self.logger.debug("Ajoute la présentation \
\"{presentation}\" au contrôleur".format(
                presentation=presentation
                ))

    def _apply_repartitions(self, repartitions_file):
        """Extraire les données de repartitions.

        Args:
            repartitions_file (unicode): fichier de configuration pour charger
                la liste CSV des repartitions, qui contient l'affectation de
                chaque présentation dans les sessions.
        """
        # lire les fichiers CSV
        repartitions = CSVDict()
        repartitions.read(repartitions_file)

        # parcours de chaque timing
        # On lit les lignes du fichier des repartitions. Le fichier doit avoir une
        # ligne par présentation. On repère les présentations avec le code.
        for timing in repartitions:
            # on récupère la présentation correspondante avec le code
            code = timing['code']
            presentation = self._get_presentation_by_code(code)

            # Si aucune présentation ne correspond au code, logger l'erreur et
            # continuer.
            if presentation is None:
                self.logger.warning("La ligne de répartiton des timings \
\"{code}\" ne correspond à aucune présentation".format(
                    code=code
                    ))

                continue

            # Si la présentation n'est affiliée à aucun jour, logger l'erreur et
            # continuer.
            if not timing['day']:
                self.logger.error("La ligne de timing \"{code}\" \
n'est attribuée à aucun jour".format(
                    code=code
                    ))

                continue

            # ajouter les infos de timing à la présentation
            presentation.day = int(timing['day'])
            presentation.session_number = int(timing['session'])
            presentation.order = int(timing['order'])
            presentation.duration = timedelta(
                    minutes=int(timing['length'])
                    )

            self.logger.debug("Ajoute les infos de timing à la présentation \
\"{presentation}\"".format(presentation=presentation))

    def _sort_events(self):
        """Trier les évents.

        Les évents sont triés par date de début.

        """
        # ordonner les évents par heure de début
        self.events.sort(key=lambda s: s.start)

    def _sort_presentations(self):
        """Affecte les présentations aux sessions et les trie.

        Au sein de chaque session, les présentations ston triées par leur numéro
        d'ordre, puis leur date de début et de fin leur sont uttribuées.

        """
        # répartir les présentations par session et les trier par ordre
        for session in self.events:
            # ne sélectionner que les sessions
            if not isinstance(session, Session):
                continue

            # récupérer les présentations qui sont associées à cette session
            presentations = self._get_presentations_by_session_number(
                    session.number
                    )

            # trier les présentations par ordre
            presentations.sort(key=lambda p: p.order)

            # affecter les temps aux présentations
            # À présent, entrer les temps de début et de fin de chaque
            # présentation selon leur durée et l'heure de début.
            start = session.start
            stop = start
            for presentation in presentations:
                # temps de début
                presentation.start = start

                # temps de fin
                stop = start + presentation.duration
                presentation.stop = stop

                # ajouter la présentation à la session
                session.add_presentation(presentation)

                # la fin de la présentation devient le début de la suivante
                start = stop

            # vérifier que la fin de la dernière présentation ne dépasse pas le
            # temps de fin de la session
            if stop > session.stop:
                raise ValueError("La fin de la dernière présentation de \
\"{session}\" a lieu après l'heure de fin de cette session".format(
                        session=session
                        ).encode(sys.stderr.encoding))

    def _get_presentations_by_session_number(self, number):
        """Retourne une liste de présentations de la même session.

        Args:
            number (int): numéro de session.

        Returns:
            :obj:`list` of :obj:`Presentation`: liste de présentations associées
            à cette session.

        """
        return [p for p in self.presentations if p.session_number == number]

    def _get_presentation_by_code(self, code):
        """Retourne une présentation par son code.

        Args:
            code (str): code unique de la présentation.

        Returns:
            :obj:`Presentation`: présentation correspondante.

        """
        for presentation in self.presentations:
            if presentation.code == code:
                return presentation

        return None
