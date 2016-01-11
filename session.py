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

package_path = os.path.dirname(os.path.realpath(__file__))


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
    template_file_path = os.path.join(package_path, SESSION_DIRECTORY, template_file)
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


class Session(object):
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

    def __unicode__(self, body_template=session_body_template, header_template=session_header_template):
        # header
        header_str = header_template.substitute(
                color=self.color,
                number=self.number,
                start=self.start.strftime(STRF_TIME),
                stop=self.stop.strftime(STRF_TIME),
                presentator=self.presentator
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
        body_str = body_template.substitute(
                items=items_str
                )
        # session
        session_str = session_template.substitute(
                header=header_str,
                body=body_str
                )
        return session_str

class SessionPresentation(object):
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

    def __unicode__(self, template=session_item_template):
        presentation_str = template.safe_substitute(
                start=self.start.strftime(STRF_TIME),
                stop=self.stop.strftime(STRF_TIME),
                title=self.phd.title,
                presentator=self.student.name,
                supervizors=', '.join([unicode(s) for s in self.phd.supervizors]),
                grade=self.student.grade,
                origin=self.student.department + '/' + self.student.unit \
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
