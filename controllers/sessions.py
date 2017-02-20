#-*- coding: utf8 -*-
from __future__ import unicode_literals
import os
import logging
from datetime import timedelta, datetime
from codecs import open
from ConfigParser import SafeConfigParser
from colour import Color
from jdd import BasicController
from ..utils import utils
from ..utils.csv_dict import CSVDict
from ..models.sessions import Session, SessionPresentation
from ..models.jdd import Student, PhD, Supervizor, Director
from ..views.sessions import SessionsView
from ..config import config


DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = DATE_FORMAT + ' ' + TIME_FORMAT


class SessionsController(BasicController):
    """ Contrôleur pour la génération du fichier de sessions

        Le contrôleur donne accès aux méthodes pour la génération des fichiers
        de sessions. La méthode `create` récupère les données des fichiers
        d'entrée, puis les ordonne avec les classes des modèles.  La méthode
        `retrieve` exporte les données stockées par la vue.

        Attributes:
            logger (:obj:`logging.Logger`): logger pour toute la classe.
            presentations (:obj:`list` of :obj:`SessionPresentation`): liste
                des présentations.
            sessions (:obj:`list` of :obj:`sessions`): liste des sessions.
            sessions_text (:obj:`list` of :obj:`str`): liste des sessions
                sous forme de texte formaté.
    """
    logger = logging.getLogger('controllers.sessions.SessionsController')

    def __init__(self):
        self.presentations = []
        self.sessions = []
        self.sessions_text = []

    def create(self, listing_file, timings_file, sessions_file):
        """ Crée la structure de donnée depuis les différents fichiers
            d'entrée.

            Args:
                listing_file (unicode): fichier de configuration pour charger
                    le listing CVS des doctorants, qui doit contenir les sujets,
                    les doctorants et les encadrants.
                timings_file (unicode): fichier de configuration pour charger
                    le listing CVS des timings, qui contient l'affectation de
                    chaque présentation dans les sessions.
                sessions_file (unicode): fichies de configuration des sessions
                    qui contient pour chaque session leur jour, heure, chairman
                    et couleur d'affichage sur le programme.
        """
        # créer les présentations
        self._create_presentations(listing_file)

        # créer les timings
        self._create_timings(timings_file)

        # créer les sessions
        self._create_sessions(sessions_file)

        # assigner les présentations dans l'ordre aux sessions
        self._manage_sessions()

    def _create_presentations(self, listing_file):
        """ Extraire les données de présentations

            Args:
                listing_file (unicode): fichier de configuration pour charger
                    le listing CVS des doctorants, qui doit contenir les sujets,
                    les doctorants et les encadrants.
        """
        # lire le fichier CSV
        listing = CSVDict()
        listing.read(listing_file)

        # créer les objets
        self.presentations = []

        # lire chaque ligne
        # On lit les lignes du fichier qui liste les doctorants avec leur sujet
        # et leur encadrants/directeurs. On considère que chaque ligne donne
        # une présentation.
        for line in listing:
            # On ajoute une nouvelle présentation que si elle sera présentée.
            if config.getboolean('booleans', line['come'].lower()):
                # présentation
                presentation = SessionPresentation(
                        code=line['code'],
                        )

                # doctorant
                student = Student(
                        name=(
                            line['first-name'] + ' ' + line['name']
                            ).title(),

                        grade=line['grade'],
                        department=line['department'],
                        unit=line['unit'],
                        location=line['location'],
                        )

                # encadrants
                # On charge tous les encadrants possibles comme on ne connait
                # pas leur nombre, on utilise une boucle infinie.
                # Ceci marche car les champs concernant les encadrants dans le
                # fichier de configuration sont préfixés du numéro d'encadrant :
                # `s1-name` avec `s` pour "supervizor".
                supervizors = []
                i = 0
                while True:
                    # On vérifie que le nom de l'encadrant suivant existe et
                    # n'est pas vide.
                    # TODO commencer à 0
                    i += 1
                    if "s{}-name".format(i) not in line or \
                            not line["s{}-name".format(i)]:
                                break

                    # dans ce cas ajouter l'encadrant
                    prefix = 's{}-'.format(i)
                    supervizors.append(Supervizor(
                        title=line[prefix + 'title'],
                        name=line[prefix + 'name'].title(),
                        origin=line[prefix + 'origin'],
                        department=line[prefix + 'department'],
                        unit=line[prefix + 'unit']
                        ))

                # directeurs
                # Même logique que pour les encadrants.  Sauf que les champs
                # concernant les directeurs sont préfixés par `d`, pour
                # "director": `d1-name`.
                directors = []
                i = 0
                while True:
                    # On vérifie que le nom du directeur suivant existe et n'est
                    # pas vide.
                    i += 1
                    if "d{}-name".format(i) not in line or \
                            not line["d{}-name".format(i)]:
                                break

                    # dans ce cas ajouter le directeur
                    prefix = 'd{}-'.format(i)
                    directors.append(Director(
                        title=line[prefix + 'title'],
                        name=line[prefix + 'name'].title(),
                        origin=line[prefix + 'origin']
                        ))

                # thèse
                phd = PhD(
                        title=line['title'],
                        funding=line['funding'],
                        )

                # faire les liens entre les objets
                phd.set_student(student)
                phd.add_supervizors(supervizors)
                phd.add_directors(directors)
                presentation.set_phd(phd)

                # sauver
                self.presentations.append(presentation)
                self.logger.debug("Ajoute la présentation \
\"{presentation}\" au contrôleur".format(
                    presentation=presentation
                    ))

    def _create_timings(self, timings_file):
        """ Extraire les données de timings

            Args:
                timings_file (unicode): fichier de configuration pour charger
                    le listing CVS des timings, qui contient l'affectation de
                    chaque présentation dans les sessions.
        """
        # lire les fichiers CSV
        timings = CSVDict()
        timings.read(timings_file)

        # parcours de chaque timing
        # On lit les lignes du fichier des timings. Le fichier doit avoir une
        # ligne par présentation on repère les présentations avec le code.
        for timing in timings:
            # on récupère la présentation correspondante avec le code
            code = timing['code']
            presentation = self._get_presentation_by_code(code)

            # Si aucune présentation ne correspond au code, logger l'erreur et
            # continuer.
            if presentation is None:
                self.logger.warning("La ligne de timing \"{code}\" \
ne correspond à aucun code de présentation".format(
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
            presentation.session = int(timing['session'])
            presentation.order = int(timing['order'])
            presentation.duration = timedelta(
                    minutes=int(timing['length'])
                    )

            self.logger.debug("Ajoute les infos de timing à la présentation \
\"{presentation}\"".format(presentation=presentation))

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

    def _manage_sessions(self):
        """ Affecte les présentations aux sessions et trie
            tout le monde
        """
        # ordonner les sessions par numéro de session
        self.sessions.sort(key=lambda s: s.number)

        # répartir les présentations par session et les trier par ordre
        for session in self.sessions:
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

            # entrer le temps de fin de la session
            session.stop = stop + session.extra

    def _get_presentations_by_session_number(self, number):
        """ Retourne une liste de présentations de la même session

            Args:
                number (int): numéro de session.

            Returns:
                :obj:`list` of :obj:`SessionPresentation`: liste
                de présentations associées à cette session.
        """
        return [p for p in self.presentations if p.session == number]

    def _get_presentation_by_code(self, code):
        """ Retourne une présentation par son code

            Args:
                code (str): code unique de la présentation.

            Returns:
                :obj:`SessionPresentation`: présentation correspondante.
        """
        for presentation in self.presentations:
            if presentation.code == code:
                return presentation

        return None

    def retrieve(self, directory):
        """ Donne une représentation des sessions en passant par la vue

            Args:
                directory (unicode): dossier de sortie où enregistrer les
                    fichiers.
        """
        # rendre en template
        self._templetize_sessions()

        # dossier pour les sessions
        directory_complete = os.path.join(
                directory,
                'sessions'
                )

        # écrire
        self._write_texts(self.sessions_text, directory_complete)
        self._write_text(self.sessions_container_text, directory_complete)

    def _templetize_sessions(self):
        """ Appelle la vue pour formater les données
        """
        # crée une vue et lui passe les données
        view = SessionsView()
        self.sessions_text = view.retrieve_sessions(self.sessions)
        self.sessions_container_text = view.retrieve_sessions_container(
                self.sessions_text,
                self.sessions
                )
