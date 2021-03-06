#-*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import logging
from datetime import datetime, timedelta

from colour import Color

from .jdd import PhD, Supervizor


class Event(object):
    """Classe d'un évent du planning.

    Un évent (ou événement en bon français) est une entrée du planning. Il peut
    s'agir d'une session de présentations, d'une pause, d'un discours...
    N'importe quelle entrée du planning est un évent représenté par cette
    classe. Cependant, pour les évents plus complexes, on utilise des classe
    spécialisées qui héritent de la classe `Event`. C'est le cas pour les
    sessions de présentations qui sont des évents représentés par la classe
    `Session`.

    Attributes:
        logger (:obj:`logging.Logger`): logger pour toute la classe.
        event_type (unicode): type d'évent.
        name (unicode): nom de l'évent.
        number (int): numéro de l'évent. Le numéro est utilisé quand nécessaire
            pour distinguer deux évents avec le même nom.
        color (:obj:`colour.Color`): couleur dans le programme.
        day (:obj:`datetime.datetime`): jour de l'évent.
        start (:obj:`datetime.datetime`): heure et jour du début de l'évent.  Ça
            peut sembler overkill d'inclure le jour, en fait il est plus facile
            de manipuler un jour+heure que l'heure seule avec le module
            `datetime`.
        stop (:obj:`datetime.datetime`): heure et jour de la fin de l'évent.
        chairman (unicode): présentateur/responsable de l'évent. Son nom est
            affiché dans le programme.

    Args:
        name (unicode): nom de l'évent.
        number (int): numéro de l'évent.
        color (:obj:`colour.Color`): couleur dans le programme.
        chairman (unicode): présentateur/responsable de l'évent.
        day (:obj:`datetime.datetime`): jour de l'évent.
        start (:obj:`datetime.datetime`): heure et jour du début de l'évent.
            Voir la note dans le bloc sur les attributs.
        stop (:obj:`datetime.datetime`): heure et jour de la fin de l'évent.

    """
    logger = logging.getLogger('models.planning.Event')
    event_type = 'event'

    def __init__(
            self,
            name,
            number=0,
            color=None,
            chairman="",
            day=None,
            start=None,
            stop=None
            ):

        self.name = name
        self.number = number
        self.color = color or Color('red')
        self.day = day or datetime.today()
        self.start = start or datetime.today()
        self.stop = stop or datetime.today()
        self.chairman = chairman

    def __unicode__(self):
        if self.number:
            return unicode("{} {}".format(self.name, self.number))

        return unicode(self.name)


class Session(Event):
    """Classe d'une session.

    Une session désigne un groupe de présentations entre deux pauses, avec le
    même chairman. Une session est un événement, c'est pourquoi elle hérite de
    la classe `Event`.

    Attributes:
        logger (:obj:`logging.Logger`): logger pour toute la classe.
        event_type (unicode): type d'évent. Ici une session.
        name (unicode): nom de l'évent, obligatoirement `Session`.
        number (int): numéro de la session. Le numéro est utilisé pour affecter
            les présentations depuis le fichier de timings avec la colonne
            `Session`.
        color (:obj:`colour.Color`): couleur dans le programme.
        day (:obj:`datetime.datetime`): jour de la session.
        start (:obj:`datetime.datetime`): heure et jour du début de la session.
            Ça peut sembler overkill d'inclure le jour, en fait il est plus
            facile de manipuler un jour+heure que l'heure seule avec le module
            `datetime`.
        stop (:obj:`datetime.datetime`): heure et jour de la fin de la session.
        chairman (unicode): présentateur de la session.
        presentations (:obj:`list` of :obj:`Presentation`): liste des
            présentations le la session.

    Args:
        number (int): numéro de la session.
        color (:obj:`colour.Color`): couleur dans le programme.
        chairman (unicode): présentateur de la session.
        day (:obj:`datetime.datetime`): jour de la session.
        start (:obj:`datetime.datetime`): heure et jour du début de la session.
            Voir la note dans le bloc sur les attributs.
        stop (:obj:`datetime.datetime`): heure et jour de la fin de la session.

    """
    logger = logging.getLogger('models.planning.Session')
    event_type = 'session'

    def __init__(self, *args, **kwargs):
        # appel du constructeur parent
        super(Session, self).__init__(name="Session", *args, **kwargs)

        # liste des présentations
        self.presentations = []

    @property
    def presentations_amount(self):
        """int: nombre de présentations dans la session.

        """
        return len(self.presentations)

    def add_presentation(self, presentation):
        """Ajouter une présentation à la session.

        Args:
            presentation (:obj:`Presentation`): présentation à ajouter.

        """
        # on vérifie que la présentation à ajouter est le bon objet
        if not isinstance(presentation, Presentation):
            raise ValueError("La présentation doit être un objet \
Presentation".encode(sys.stderr.encoding))

        # on l'ajoute à la fin
        self.presentations.append(presentation)
        self.logger.debug('Ajoute la présentation "{presentation}" à \
la "{session}"'.format(
            presentation=presentation,
            session=self
            ))

    def remove_presentation(self, id):
        """Enlever une présentation à la session.

        Args:
            id (int): index de la présentation à supprimer.

        Returns:
            :obj:`Presentation`: présentation enlevée.

        """
        # on vérifie que l'index est valide
        amount = self.presentations_amount
        if not -amount <= id < amount:
            raise IndexError("L'index de présentation demandé n'existe \
pas".encode(sys.stderr.encoding))

        # on enlève la présentation
        self.logger.debug('Supprime la présentation "{presentation}" de \
la "{session}"'.format(
            presentation=self.presentations[id],
            session=self
            ))

        return self.presentation.pop(id)


class Presentation(object):
    """Classe d'une présentation.

    Une présentation désigne le passage du candidat. Elle est décrite du point
    de vue technique comme un moment où une thèse est présentée.

    Attributes:
        code (unicode): code unique pour désigner la présentation.
        phd (:obj:`PhD`): thèse à présenter.
        duration (:obj:`datetime.timedelta`): durée de la présentation.
        start (:obj:`datetine.datetine`): jour et heure de début.
        stop (:obj:`datetine.datetine`): jour et heure de fin.
        session_number (int): numéro de session. Permet de relier à une session
            par son attribut `number`.
        day (int): numéro du jour de passage, pour relier avec le fichier de
            timings.
        order (int): ordre de passage dans la session.

    Args:
        code (unicode): code unique pour désigner la présentation.
        duration (:obj:`datetime.timedelta`): durée de la présentation.
        start (:obj:`datetine.datetine`): jour et heure de début.
        stop (:obj:`datetine.datetine`): jour et heure de fin.
        session_number (int): numéro de session.
        day (int): numéro du jour de passage.
        order (int): ordre de passage dans la session.

    """
    logger = logging.getLogger('models.planning.Presentation')

    def __init__(
            self,
            code,
            duration=None,
            start=None,
            stop=None,
            session_number=0,
            day=0,
            order=0
            ):

        self.code = code
        self.phd = None
        self.duration = duration
        self.start = start or datetime.today()
        self.stop = stop or datetime.today()
        self.session_number = int(session_number)
        self.day = int(day)
        self.order = int(order)

    def __unicode__(self):
        return unicode(self.code)

    def set_phd(self, phd):
        """Affecte une thèse à la présentation.

        Args:
            phd (:obj:`Phd`): thèse à ajouter.

        """
        # vérifier que le phd est un objet valide
        if not isinstance(phd, PhD):
            raise ValueError("La thèse doit être un objet \
PhD".encode(sys.stderr.encoding))

        # ajouter l'objet
        self.phd = phd
        self.logger.debug('Ajoute la thèse "{phd}" à la \
présentation "{presentation}"'.format(
            phd=phd,
            presentation=self
            ))

    def remove_phd(self):
        """Désaffecteur une thèse à la présentation.

        Returns:
            :obj:`PhD`: thèse désaffectée.

        """
        # conserver la thèse pour la retourner à la fin de la fonction
        phd = self.phd

        # supprimer l'objet
        self.logger.debug('Supprime la thèse "{phd}" de la \
présentation "{presentation}"'.format(
            phd=self.phd,
            presentation=self
            ))

        self.phd = None
        return phd
