#-*- coding: utf8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

import os
import sys
import logging

from colour import Color

from .jdd import PhD


class Section(object):
    """Classe pour un ensemble de résumés courts d'une session.

    Les différents résumés courts sont regroupés par sessions, on appelle ces
    regroupements les sections du recueil.

    Attributes:
        logger (:obj:`logging.Logger`): logger pour l'instance de la classe.
        number (int): numéro de la section, qui sert à regrouper les résumés par
            leur numéro de session. En clair, le numéro de session d'une thèse
            dans le planning est le numéro de sa section dans le recueil.
        abstracts (:obj:`list` of :obj:`Abstract`): liste des objets résumés.
        color (:obj:`colour.Color`): couleur du bandeau de chaque résumé dans la
            section.

    Args:
        number (int): numéro de la section.
        color (:obj:`colour.Color`): couleur du bandeau de chaque résumé dans la
            section.

    """
    logger = logging.getLogger('models.booklet.Section')

    def __init__(self, number=0, color=None):
        self.number = number
        self.abstracts = []
        self.color = color or Color('red')

    def __unicode__(self):
        return "Section {}".format(self.number)

    @property
    def abtracts_amount(self):
        """int: nombre de résumés pour cette section.

        """
        return len(self.abstracts)

    def add_abstract(self, abstract):
        """Ajoute un objet résumé à la section.

        Le résumé est ajouté à la fin de la liste.

        Args:
            abstract (:obj:`Abstract`): résumé à ajouter.
        """
        if not isinstance(abstract, Abstract):
            raise ValueError("Le résumé doit être un objet \
Abstract".encode(sys.stderr.encoding))

        self.abstracts.append(abstract)
        self.logger.debug("Ajoute le résumé \"{abstract}\" à la section \
\"{section}\"".format(
                abstract=abstract,
                section=self
                ))

    def remove_abstract(self, id):
        """Supprimer un résumé de la section.

        Args:
            id (int): index du résumé à supprimer.

        Returns:
            :obj:`Abstract`: résumé supprimé de la section.
        """
        amount = self.abtracts_amount
        if not -amount <= id < amount:
            raise IndexError("L'index de résumé demandé n'existe \
pas".encode(sys.stderr.encoding))

        self.logger.debug("Supprime le résumé \"{abstract}\" de la section \
\"{section}\"".format(
                abstract=self.abstract[id],
                section=self
                ))

        return self.abstracts.pop(id)


class Abstract(object):
    """Classe pour un résumé court.


    Attributes:
        logger (:obj:`logging.Logger`): logger pour l'instance de la classe.
        code (unicode): identifiant unique du résumé.
        text (unicode): résumé proprement dit.
        keywords (:obj:`list` of unicode): liste des mots-clés.
        section (int): numéro de section à laquelle appartient le résumé.
        order (int): numéro du résumé dans la section. Il s'agit du même ordre
            que pour le passage dans le planning.
        color (:obj:`colour.Color`): couleur du bandeau du résumé.
        phd (:obj:`PhD`): thèse attachée au résumé.

    Args:
        code (unicode): identifiant unique du résumé.
        keywords (:obj:`list` of unicode): liste des mots-clés.
        text (unicode): résumé proprement dit.
        color (:obj:`colour.Color`): couleur du bandeau du résumé.
        section (int): numéro de section à laquelle appartient le résumé.
        order (int): numéro du résumé dans la section.

    """
    logger = logging.getLogger('models.booklet.Abstract')

    def __init__(
            self,
            code,
            keywords=[],
            text="",
            color=Color('red'),
            section=0,
            order=0
            ):

        self.code = code
        self.text = text
        if not isinstance(keywords, (list, tuple)):
            keywords = [keywords]

        self.keywords = keywords
        self.section = section
        self.order = order
        self.color = color
        self.phd = None

    def __unicode__(self):
        if len(self.text) > 30:
            return unicode(self.text)[:30].strip() + '...'

        else:
            return unicode(self.text)

    def set_phd(self, phd):
        """Affecte une thèse au résumé.

        Args:
            phd (:obj:`Phd`): thèse à ajouter.

        """
        # vérifier que le phd est un objet valide
        if not isinstance(phd, PhD):
            raise ValueError("La thèse doit être un objet \
PhD".encode(sys.stderr.encoding))

        # ajouter l'objet
        self.phd = phd
        self.logger.debug('Ajoute la thèse "{phd}" au \
résumé "{abstract}"'.format(
            phd=phd,
            abstract=self
            ))

    def remove_phd(self):
        """Désaffecteur une thèse au résumé.

        Returns:
            :obj:`PhD`: thèse désaffectée.

        """
        # conserver la thèse pour la retourner à la fin de la fonction
        phd = self.phd

        # supprimer l'objet
        self.logger.debug('Supprime la thèse "{phd}" du \
résumé "{abstract}"'.format(
            phd=self.phd,
            abstract=self
            ))
