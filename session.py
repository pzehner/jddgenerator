#-*- coding: utf8 -*-

""" Classe pour la génération du programme des JDD
"""


##
# imports
#


from __future__ import unicode_literals
from codecs import open
from string import Template
import datetime
import locale
import os
from jdd import Supervizor, Student, PhD


##
# constantes
#


SESSION_DIRECTORY = "session_files"
SESSION_BODY_FILE = 'session_body.tex'
SESSION_HEADER_FILE = 'session_header.tex'
SESSION_ITEM_FILE = 'session_item.tex'
SESSION_ITEM_SEPARATOR_FILE = 'session_item_separator.tex'
SESSION_FILE = "session.tex"
STRF_TIME = "%H:%M"


##
# paramètres
#


locale.setlocale(locale.LC_ALL, b'fr_FR')


##
# charge les templates
#


def load_template(template_file):
    template_file_path = os.path.join(SESSION_DIRECTORY, template_file)
    with open(template_file_path, 'r', encoding='utf8') as file:
        return file.read()

try:
    session_body_template = Template(load_template(SESSION_BODY_FILE))
    session_header_template = Template(load_template(SESSION_HEADER_FILE))
    session_template = Template(load_template(SESSION_FILE))
    session_item_template = Template(load_template(SESSION_ITEM_FILE))
    session_item_separator = load_template(SESSION_ITEM_SEPARATOR_FILE)
except Exception:
    message = "Erreur à l'ouverture des fichiers de template"
    print message
    raise


##
# classes
#


class Session:
    """ Classe d'une session
    """

    def __init__(self, number, color, presentator, presentations, \
            day=None, start=None, stop=None):
        self.number = number
        self.color = color
        self.day = day
        self.start = start if start is not None else datetime.datetime.today()
        self.stop = stop if stop is not None else datetime.datetime.today()
        self.presentator = presentator
        if presentations and type(presentations) is list:
            presentation0 = presentations[0]
            if type(presentation0) is tuple:
                self.presentations = [SessionPresentation(*p) for p in presentations]
            else:
                self.presentations = presentations
        else:
            self.presentations = ""

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        # header
        header_str = session_header_template.substitute(
                session_color=self.color,
                session_number=self.number,
                session_start=self.start.strftime(STRF_TIME),
                session_stop=self.stop.strftime(STRF_TIME),
                session_presentator=self.presentator
                )
        # body
        items_str = ""
        first = True
        for item in self.presentations:
            if not first:
                items_str += session_item_separator
            else:
                first = False
            items_str += unicode(item)
        body_str = session_body_template.substitute(
                session_items=items_str
                )
        # session
        session_str = session_template.substitute(
                session_header=header_str,
                session_body=body_str
                )
        return session_str

class SessionPresentation():
    """ Classe d'une présentation
    """

    def __init__(self, code, title, presentator, grade, department, unit, supervizors, \
            duration=None, start=None, stop=None, session=0, day=None, order=0):
        self.code = code
        self.student = Student(
                name=presentator,
                grade=grade,
                department=department,
                unit=unit
                )
        self.phd = PhD(
                title=title,
                supervizors=supervizors
                )
        for supervizor in self.phd.supervizors:
            supervizor.__class__ = SessionPresentationSupervizor

        self.duration = duration
        self.start=start if start is not None else datetime.datetime.today()
        self.stop=start if stop is not None else datetime.datetime.today()
        self.session = int(session)
        self.day = day
        self.order = int(order)

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        presentation_str = session_item_template.substitute(
                session_item_start=self.start.strftime(STRF_TIME),
                session_item_stop=self.stop.strftime(STRF_TIME),
                session_item_title=self.phd.title,
                session_item_presentator=self.student.name,
                session_item_supervizors=', '.join([unicode(s) for s in self.phd.supervizors]),
                session_item_grade=self.student.grade,
                session_item_origin=self.student.department + '/' + self.student.unit \
                        if self.student.unit else self.student.department
                )
        return presentation_str

class SessionPresentationSupervizor(Supervizor):
    """ Classe des encadrants et directeurs
    """

    def __unicode__(self):
        string = ""
        string += self.title + '~' if self.title else ''
        string += self.name
        string += ' (\small{' + self.origin + '})' if self.origin else ''
        return string
