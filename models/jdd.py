# -*- coding: utf8 -*-


""" Classes génériques pour les JDD
"""


##
# imports
#


from __future__ import unicode_literals


##
# classes
#


class Student(object):
    """ Classe du doctorant
    """

    def __init__(self, name, grade, department, unit, \
            location="", email="", picture=""):
        self.name = name
        self.grade = grade
        self.department = department.strip()
        self.unit = unit.strip()
        self.email = email
        self.picture = picture

        location_lower = location.lower()
        if location_lower == "cc":
            self.location = "Centre de Châtillon"
        elif location_lower == "cm":
            self.location = "Centre de Meudon"
        elif location_lower == "cp":
            self.location = "Centre de Palaiseau"
        elif location_lower == "cl":
            self.location = "Centre de Lilles"
        elif location_lower == "ct":
            self.location = "Centre de Toulouse"
        else:
            self.location = location

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other


    def __unicode__(self):
        return "{name} ({department}/{unit}, {grade})".format(
                name=self.name,
                grade=self.grade,
                department=self.department,
                unit=self.unit
                )

    def __str__(self):
        return unicode(self)

class PhD(object):
    """ Classe de thèse
    """

    def __init__(self, title, supervizors, \
            directors=[], funding=""):
        self.title = title
        self.funding = funding
        if directors and type(directors) in (list, tuple):
            director0 = directors[0]
            if type(director0) is tuple:
                self.directors = [Director(*s) for s in directors if any(s)]
            else:
                self.directors = directors
        else:
            self.directors = []
        if supervizors and type(supervizors) in (list, tuple):
            supervizor0 = supervizors[0]
            if type(supervizor0) is tuple:
                self.supervizors = [Supervizor(*s) for s in supervizors if any(s)]
            else:
                self.supervizors = supervizors
        else:
            self.supervizors = []

    def __hash__(self):
        return hash(self.title)

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other

    def __unicode__(self):
        return self.title

    def __str__(self):
        return unicode(self)

class Supervizor(object):
    """ Classe des encadrants
    """

    def __init__(self, title, name, origin="", department="", unit=""):
        title_lower = title.lower()
        if not title_lower:
            self.title = ""
        elif title_lower == "docteur":
            self.title = "Dr."
        elif title_lower == "docteur, avec hdr":
            self.title = "Dr. HDR"
        elif title_lower == "professeur":
            self.title = "Pr."
        elif title_lower == "maître de conférence":
            self.title = "MDC"
        elif title_lower == "ingénieur":
            self.title = "Ing."
        elif title_lower == "ingénieur de recherche":
            self.title = "Ing."
        elif title_lower == "directeur de recherche":
            self.title = "DR"
        elif title_lower == "chargé de recherche":
            self.title = "CR"
        else:
            self.title = title
        self.name = name
        self.origin = origin
        self.department = department.strip()
        self.unit = unit.strip()

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self is other

    def __ne__(self, other):
        return self is not other

    def __unicode__(self):
        output = self.title + '~' if self.title else ""
        output += self.name
        output += ' (' + self.department + '/' + self.unit + ')' \
                if self.unit else ' (' + self.department + ')' \
                if self.department else ' (' + self.origin + ')' \
                if self.origin else ''
        return output

    def __str__(self):
        return unicode(self)

class Director(Supervizor):
    """ Classe des directeurs
    """

    def __unicode__(self):
        if not self.department:
            output = self.title + '~' if self.title else ""
            output += "{name} ({origin})".format(
                    name=self.name,
                    origin=self.origin
                    )
            return output
        else:
            return super(Director, self).__unicode__()
