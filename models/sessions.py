#-*- coding: utf8 -*-

""" Classe pour la génération du programme des JDD
"""
from __future__ import unicode_literals
from datetime import datetime, timedelta
import logging
from jdd import PhD, Supervizor
from planning import Event


class Session(Event):
    """ Classe d'une session

        Une session désigne un groupe de présentations entre deux pauses,
        avec le même chairman. Une session est un événement, c'est pourquoi elle
        hérite de la classe `Event` de `Planning`.

        Attributes:
            logger (:obj:`logging.Logger`): logger pour toute la classe.
            number (int): numéro de la session. Le numéro est utilisé pour
                affecter les présentations depuis le fichier de timings avec
                la colonne `Session`.
            color (unicode): couleur dans le programme.
            day (:obj:`datetime.datetime`): jour de la session.
            start (:obj:`datetime.datetime`): heure et jour du début de la
                session. Ça peut sembler overkill d'inclure le jour, en fait
                il est plus facile de manipuler un jour+heure que l'heure
                seule avec le module `datetime`.
            stop (:obj:`datetime.datetime`): heure et jour de la fin de la
                session.
            extra (:obj:`datetime.timedelta`): temps supplémentaire à ajouter
                à la fin de la session.
            chairman (unicode): présentateur de la session.
            presentations (:obj:`list` of :obj:`SessionPresentation`): liste
                des présentations le la session.
    """
    logger = logging.getLogger('models.sessions.Session')

    def __init__(self, number,
            color=None, chairman="", day=None, start=None, stop=None, extra=None):
        self.number = number
        self.color = color
        self.day = day
        self.start = start or datetime.today()
        self.stop = stop or datetime.today()
        self.extra = extra
        self.chairman = chairman

        self.presentations = []

    def __unicode__(self):
        return unicode(self.number)

    @property
    def presentations_amount(self):
        """ int: nombre de présentations dans la session.
        """
        return len(self.presentations)

    def add_presentation(self, presentation):
        """ Ajouter une présentation à la session

            Args:
                presentation (:obj:`SessionPresentation`): présentation à
                    ajouter.
        """
        # on vérifie que la présentation à ajouter est le bon objet
        if not isinstance(presentation, SessionPresentation):
            message = "La présentation doit être un objet SessionPresentation"
            raise ValueError(message)

        # on l'ajoute à la fin
        self.presentations.append(presentation)
        self.logger.debug('Ajoute la présentation "{presentation}" à la session "{session}"'.format(
            presentation=presentation,
            session=self
            ))

    def remove_presentation(self, id):
        """ Enlever une présentation à la session

            Args:
                id (int): index de la présentation à supprimer.

            Returns:
                :obj:`SessionPresentation`: présentation enlevée.
        """
        # on vérifie que l'index est valide
        amount = self.presentations_amount
        if not -amount <= id < amount:
            message = "L'index de présentation demandé n'existe pas"
            raise IndexError(message)

        # on enlève la présentation
        self.logger.debug('Supprime la présentation "{presentation}" de la session "{session}"'.format(
            presentation=self.presentations[id],
            session=self
            ))

        return self.presentation.pop(id)


class SessionPresentation(object):
    """ Classe d'une présentation

        Une présentation désigne le passage du candidat. Elle est décrite
        du point de vue technique comme un moment où une thèse est présntée.

        Attributes:
            code (unicode): code unique pour désigner la présentation.
            phd (:obj:`PhD`): thèse à présenter.
            duration (:obj:`datetime.timedelta`): durée de la présentation.
            start (:obj:`datetine.datetine`): jour et heure de début.
            stop (:obj:`datetine.datetine`): jour et heure de fin.
            session_number (int): numéro de session. Permet de relier à une
                session par son attribut `number`.
            day (int): numéro du jour de passage, pour relier avec le fichier
                de timings.
            order (int): ordre de passage dans la session.
    """
    logger = logging.getLogger('models.sessions.SessionPresentation')

    def __init__(self, code, duration=None, start=None, stop=None, session_number=0, day=0, order=0):
        self.code = code
        self.phd = PhD()
        self.duration = duration
        self.start = start or datetime.today()
        self.stop = stop or datetime.today()
        self.session_number = int(session_number)
        self.day = int(day)
        self.order = int(order)

    def __unicode__(self):
        return unicode(self.code)

    def set_phd(self, phd):
        """ Affecte une thèse à la présentation

            Args:
                phd (:obj:`Phd`): thèse à ajouter.
        """
        # vérifier que le phd est un objet valide
        if not isinstance(phd, PhD):
            message = "La thèse doit être un objet PhD"
            raise ValueError(message)

        # ajouter l'objet
        self.phd = phd
        self.logger.debug('Ajoute la thèse "{phd}" à la présentation "{presentation}"'.format(
            phd=phd,
            presentation=self
            ))

    def remove_phd(self):
        """ Désaffecteur une thèse à la présentation

            Returns:
                :obj:`PhD`: thèse désaffectée.
        """
        # conserver la thèse pour la retourner à la fin de la fonction
        phd = self.phd

        # supprimer l'objet
        self.logger.debug('Supprime la thèse "{phd}" de la présentation "{presentation}"'.format(
            phd=self.phd,
            presentation=self
            ))

        self.phd = PhD()
        return phd
