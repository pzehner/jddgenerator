#-*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from datetime import timedelta, datetime
from sessions import SessionsController
from colour import Color
from jdd import BasicController
from ..utils.csv_dict import CSVDict
from ..models.planning import Event
from ..models.sessions import Session

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = DATE_FORMAT + ' ' + TIME_FORMAT

class PlanningController(BasicController):
    logger = logging.getLogger('controllers.planning.PlanningController')

    def __init__(self):
        self.events = []
        self.events_text = []

    def create(self, planning_file):
        planning = CSVDict()
        planning.read(planning_file)

        self.events = []
        for event in planning:
            # extraction de certains paramètres en avance
            # jour de l'évent
            # On doit convertir les `/` en `-` parce que Libre Office Calc est
            # un connard qui comprent pas l'ISO 8601. Il l'encode avec des `/`
            # au lieu de `-`.
            day_str = event['day'].replace('/', '-')
            day = datetime.strptime(
                    day_str,
                    DATE_FORMAT
                    )

            # début de l'évent
            # On recrée une date complète jour + heure et pas seulement l'heure,
            # c'est plus facile à manipuler avec le module `datetime`.
            start_str = event['start-time']
            start = datetime.strptime(
                    day_str + ' ' + start_str,
                    DATETIME_FORMAT
                    )

            # fin de l'évent
            # même astuce que pour le début de l'évent
            stop_str = event['stop-time']
            stop = datetime.strptime(
                    day_str + ' ' + stop_str,
                    DATETIME_FORMAT
                    )

            # couleur du bandeau de l'évent
            # Le module colour permet plusieurs représentations de la couleur,
            # on permet ici que chaque mode soit accepté.
            color_mode = event['color-mode']
            color_value = event['color']
            color = Color(**{
                color_mode: color_value \
                        if color_value.startswith('#') \
                        else utils.read_tuple(color_value),
                })

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
                event_object = Event(
                        name=event['type'].title(),
                        number=int(event['number']),
                        color=color,
                        day=day,
                        start=start,
                        stop=stop,
                        chairman=event['chairman']
                        )

            self.events.append(event_object)
            self.logger.debug("Ajoute l'événement {} au planning".format(
                event_object
                ))

    def _create_sessions(self, sessions_file):
        """ Créer les sessions depuis la configuration

            Args:
                sessions_file (unicode): fichies de configuration des sessions
                    qui contient pour chaque session leur jour, heure, chairman
                    et couleur d'affichage sur le programme.
        """
        # vérifier que le fichier de config des sessions est valide
        if not os.path.isfile(sessions_file):
            message = "Le fichier de paramètres des sessions \"{file}\" \
n'a pas été trouvé".format(
                    file=sessions_file
                    )

            raise IOError(message)

        # charger les paramètres sur les sessions
        sessions_conf = SafeConfigParser()
        sessions_conf.read(sessions_file)

        # créer les objets
        self.sessions = []

        # parcourir les sessions
        # On lit le fichier de paramètres des sessions section par section. On
        # s'attend à avoir autant de sections que de sessions, les sections ont
        # pour valeur (entre crochets dans le fichier) le numéro de la session.
        for session_number in sessions_conf.sections():
            # extraction de certains paramètres en avance
            day_str = sessions_conf.get(session_number, 'day').replace('/', '-')
            day = datetime.strptime(
                    day_str,
                    DATE_FORMAT
                    )

            # début de la session
            # On recrée une date complète jour + heure et pas seulement l'heure,
            # c'est plus facile à manipuler avec le module `datetime`.
            start_str = sessions_conf.get(session_number, 'start-time')
            start = datetime.strptime(
                    day_str + ' ' + start_str,
                    DATETIME_FORMAT
                    )

            # temps supplémentaire à ajouter à la fin de la session
            extra = timedelta(
                    minutes=sessions_conf.getint(session_number, 'extra-time')
                    )

            # couleur du bandeau de la session
            # colour permet plusieurs représentations de la couleur, on permet
            # ici que chaque mode soit accepté
            color_mode = sessions_conf.get(session_number, 'color-mode')
            color_value = sessions_conf.get(session_number, 'color')
            color = Color(**{
                color_mode: color_value \
                        if color_value.startswith('#') \
                        else utils.read_tuple(color_value),
                })

            # création de la session
            session = Session(
                    number=int(session_number),
                    color=color,
                    chairman=sessions_conf.get(session_number, 'chairman'),
                    start=start,
                    extra=extra,
                    day=day
                    )

            # sauver
            self.sessions.append(session)
            self.logger.debug("Ajoute la session \"{session}\" au \
contrôleur".format(session=session))
