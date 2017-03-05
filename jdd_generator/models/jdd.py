# -*- coding: utf8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import
import logging
from ConfigParser import NoOptionError
from ..config import config


class Student(object):
    """Classe du doctorant

    Attributes:
        logger (:obj:`logging.Logger`): logger pour toute la classe.
        name (unicode): nom et prénom.
        grade (unicode): année de thèse.
        department (unicode): département.
        unit (unicode): unité dans le département.
        email (unicode): adresse couriel interne.
        picture (unicode): nom du fichier photo. Les photos de tous les
            doctorants doivent être dans le même dossier.
        location (unicode): centre (Châtillon, Meudon...).

    Args:
        name (unicode): nom et prénom.
        grade (unicode): année de thèse.
        department (unicode): département.
        unit (unicode): unité dans le département.
        email (unicode): adresse couriel interne.
        picture (unicode): nom du fichier photo.
        location (unicode): centre (Châtillon, Meudon...). Le centre peut être
            indiqué en abrégé (CC : Centre de Châtillon, CM : Centre de
            Meudon...).  La liste des abréviations possibles (et éditable) est
            dans le fichier `config.ini` du projet.

    """
    logger = logging.getLogger('models.jdd.Student')

    def __init__(self, name="", grade="", department="", unit="", \
            location="", email="", picture="", **kwargs):
        self.name = name
        self.grade = grade
        self.department = department
        self.unit = unit
        self.email = email
        self.picture = picture
        # hack pour utiliser le property dès le constructeur
        self._location = self.location = location

    def __unicode__(self):
        return unicode(self.name)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other

    @property
    def location(self):
        """unicode: nom du centre complet.

        Le setter transforme le nom du centre abrégé en nom complet.

        """
        return self._location

    @location.setter
    def location(self, loc):
        self._location = self._format_location(loc)

    def _format_location(self, location):
        """Formate le nom des centres.

        Convertit les abbréviations de centre en nom complet selon la section
        `locations` du fichier de configuration `config.ini`. Si l'abbréviation
        n'est pas trouvée, la valeur d'entrée est retournée. Si la section
        n'existe pas ou si la section comporte une option `disabled` vraie, la
        valeur d'entrée est retournée.

        Args:
            location (unicode): nom abrégé du centre.

        Returns:
            unicode: nom complet du centre.

        """
        # si le centre n'a pas été indiqué
        if not location:
            self.logger.warning("Le centre de \"{student}\" est manquant".format(
                student=self
                ))

            return location

        # vérifier que la section des lieux existe et est activée
        if not config.has_section('locations') or \
                config.has_option('locations', 'disabled') and \
                config.getboolean('locations', 'disabled'):
                    return location

        # essayer de convertir l'abbréviation du lieu
        try:
            return config.get('locations', location.lower())

        # sinon, retourner le lieu tel quel
        except NoOptionError:
            self.logger.warning(
                    "Impossible d'expliciter le lieu \"{location}\"".format(
                        location=location
                        ))

            return location


class PhD(object):
    """Classe de thèse.

    Attributes:
        logger (:obj:`logging.Logger`): logger pour toute la classe.
        title (unicode): sujet de la thèse.
        funding (unicode): source du financement.
        directors (:obj:`list` of :obj:`Director`): liste des directeurs.
        supervizors (:obj:`list` of :obj:`Supervizor`): liste des encadrants.
        student (:obj:`Student`): doctorant attaché à cette thèse.

    Args:
        title (unicode): sujet de la thèse.
        funding (unicode): source du financement.

    """
    logger = logging.getLogger('models.jdd.PhD')

    def __init__(self, title="", funding=""):
        self.title = title
        self.funding = funding
        self.directors = []
        self.supervizors = []
        self.student = None

    def __unicode__(self):
        if len(self.title) > 30:
            return unicode(self.title)[:30].strip() + '...'

        else:
            return unicode(self.title)

    @property
    def directors_amount(self):
        """int: nombre de directeurs de thèse.

        """
        return len(self.directors)

    @property
    def supervizors_amount(self):
        """int: nombre d'encadrants.

        """
        return len(self.supervizors)

    def set_student(self, student):
        """Affecter un doctorant à la thèse.

        Args:
            student (:obj:`Student`): doctorant à affecter.

        """
        # vérifier que le doctorant est un objet valide
        if not isinstance(student, Student):
            message = "Le doctorant doit être un objet Student"
            raise ValueError(message)

        # ajouter l'objet
        self.student = student
        self.logger.debug('Ajoute le doctorant "{student}" à la thèse "{phd}"'.format(
            student=student,
            phd=self
            ))

    def remove_student(self):
        """Désaffecter le doctorant de la thèse.

        Returns:
            :obj:`Student`: doctorant désaffecté.

        """
        # récupérer l'objet pour le renvoyer à la fin de la foncion
        student = self.student

        # supprimer l'objet
        self.logger.debug('Supprime le doctorant "{student}" de la thèse {phd}'.format(
            student=self.student,
            phd=self
            ))

        self.student = None
        return student

    def add_director(self, director):
        """Ajouter un directeur de thèse.

        Args:
            director (:obj:`Director`): directeur à ajouter.

        """
        # on vérifie que le directeur est le bon objet
        if not isinstance(director, Director):
            message = "Un directeur de thèse doit être un objet Director"
            raise ValueError(message)

        # on ajoute le directeur
        self.directors.append(director)
        self.logger.debug('Ajoute le directeur "{director}" à la thèse "{phd}"'.format(
            director=director,
            phd=self
            ))

    def add_directors(self, directors):
        """Ajouter une liste de directeurs à la thèse.

        Args:
            directors (:obj:`list` of :obj:`Director`): liste des directeurs à
                ajouter.

        """
        for director in directors:
            self.add_director(director)

    def remove_director(self, id):
        """Retirer un directeur de la thèse.

        Args:
            id (int): index du directeur à retirer:

        Returns:
            :obj:`Director`: directeur retiré de la thèse.

        """
        # on vérifie que l'index est contenu dans la liste
        amount = self.directors_amount
        if not -amount <= id < amount:
            message = "L'index du directeur demandé n'existe pas"
            raise IndexError(message)

        # on supprime le directeur
        self.logger.debug('Supprime le directeur "{director}" de la thèse "{phd}"'.format(
            director=self.directors[id],
            phd=self
            ))

        return self.directors.pop(id)

    def add_supervizor(self, supervizor):
        """Ajoute un encadrant à la thèse.

        Args:
            supervizor (:obj:`Supervizor`): encadrant à ajouter.

        """
        # on vérifie que l'encadrant est le bon objet
        if not isinstance(supervizor, Supervizor):
            message = "Un encadrant doit être un objet Supervizor"
            raise ValueError(message)

        # on ajoute l'encadrant
        self.supervizors.append(supervizor)
        self.logger.debug('Ajoute l\'encadrant "{supervizor}" à la thèse "{phd}"'.format(
            supervizor=supervizor,
            phd=self
            ))

    def add_supervizors(self, supervizors):
        """Ajouter une liste d'encadrants à la thèse.

        Args:
            :obj:`list` of :obj:`Supervizor`: liste d'encadrants à ajouter.

        """
        for supervizor in supervizors:
            self.add_supervizor(supervizor)

    def remove_supervizor(self, id):
        """Retirer un directeur de la thèse.

        Args:
            id (int): undex de l'encadrant à retirer.

        Returns:
            :obj:`Supervizor`: encadrant retiré.

        """
        # on vérifie que l'index est contenu danst la liste
        amount = self.supervizors_amount
        if not -amount <= id < amount:
            message = "L'index de l'encadrant demandé n'existe pas"
            raise IndexError(message)

        # on supprime l'encadrant
        self.logger.debug('Supprime l\'encadrant "{supervizor}" de la thèse "{phd}"'.format(
            supervizor=self.supervizors[id],
            phd=self
            ))

        return self.supervizors.pop(id)

    def __hash__(self):
        return hash(self.title)

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other


class Supervizor(object):
    """Classe des encadrants.

    Attributes:
        logger (:obj:`logging.Logger`): logger pour toute la classe.
        title (unicode): titre du bonhomme.
        name (unicode): nom et prénom.
        origin (unicode): laboratoire d'origine.
        department (unicode): département où travaille l'encadrant.
        unit (unicode): unité dans le département.

    Args:
        name (unicode): nom et prénom.
        origin (unicode): laboratoire d'origine.
        department (unicode): département où travaille l'encadrant.
        unit (unicode): unité dans le département.
        title (unicode): titre du bonhomme. Les titres sont abrégés (Docteur :
            Dr., Professeur : Pr., Maître de Conférence : MDC...). La liste des
            abréviations reconnues est dans le fichier `config.ini` du projet.
    """
    logger = logging.getLogger('models.jdd.Supervizor')

    def __init__(self, title="", name="", origin="", department="", unit=""):
        self.name = name
        self.origin = origin
        self.department = department
        self.unit = unit
        # hack pour utiliser le property dans le constructeur
        self._title = self.title = title

    def __unicode__(self):
        return unicode(self.name)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other

    @property
    def title(self):
        """unicode: titre de l'encadrant.

        Le setter permet de formatter le titre en une abréviation.

        """
        return self._title

    @title.setter
    def title(self, ti):
        self._title = self._format_title(ti)

    def _format_title(self, title):
        """Formate le titre de l'encadrant.

        Convertit les noms complet de titre en abbréviation selon la section
        `titles` du fichier de configuration `config.ini`. Si le titre n'est pas
        trouvée, la valeur d'entrée est retournée. Si la section n'existe pas ou
        si la section comporte une option `disabled` vraie, la valeur d'entrée
        est retournée.

        Args:
            title (unicode): titre complet.

        Returns:
            (unicode): titre abrégé.

        """
        # si le titre n'a pas été indiqué
        if not title:
            self.logger.warning("Le titre de \"{supervizor}\" est manquant".format(
                supervizor=self
                ))

            return title

        # vérifier que la section des titres existe et est activée
        if not config.has_section('titles') or \
                config.has_option('titles', 'disabled') and \
                config.getboolean('titles', 'disabled'):
                    return title

        # essayer de convertir le titre
        try:
            return config.get('titles', title.lower())

        # sinon, retourner le titre tel quel
        except NoOptionError:
            self.logger.warning(
                    "Impossible d'abréger le titre \"{title}\"".format(
                        title=title
                        ))

            return title


class Director(Supervizor):
    """Classe des directeurs.

    Attributes:
        logger (:obj:`logging.Logger`): logger pour toute la classe.
        title (unicode): titre du bonhomme.
        name (unicode): nom et prénom.
        origin (unicode): laboratoire d'origine.
        department (unicode): département où travaille le directeur.
        unit (unicode): unité dans le département.

    Args:
        name (unicode): nom et prénom.
        origin (unicode): laboratoire d'origine.
        department (unicode): département où travaille le directeur.
        unit (unicode): unité dans le département.
        title (unicode): titre du bonhomme. Les titres sont abrégés (Docteur :
            Dr., Professeur : Pr., Maître de Conférence : MDC...). La liste des
            abréviations reconnues est dans le fichier `config.ini` du projet.

    """
    logger = logging.getLogger('models.jdd.Director')
