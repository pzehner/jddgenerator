#-*- coding: utf8 -*-

""" Classe pour la génération du programme des JDD pour les animateurs de session
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
from session import Session, SessionPresentation

package_path = os.path.dirname(os.path.realpath(__file__))


##
# constantes
#


SESSION_TIMING_DIRECTORY = "session_timing_files"
SESSION_TIMING_ITEM_FILE = 'session_timing_item.tex'
SESSION_TIMING_BODY_FILE = 'session_timing_body.tex'
SESSION_TIMING_HEADER_FILE = 'session_timing_header.tex'
STRF_TIME = '{hours}:{minutes}'


##
# paramètres
#


locale.setlocale(locale.LC_ALL, b'fr_FR')


##
# charge les templates
#


def load_template(template_file):
    template_file_path = os.path.join(package_path, SESSION_TIMING_DIRECTORY, template_file)
    with open(template_file_path, 'r', encoding='utf8') as file:
        return file.read()

try:
    session_timing_item_template = Template(load_template(SESSION_TIMING_ITEM_FILE))
    session_timing_body_template = Template(load_template(SESSION_TIMING_BODY_FILE))
    session_timing_header_template = Template(load_template(SESSION_TIMING_HEADER_FILE))
except Exception:
    message = "Erreur à l'ouverture des fichiers de template"
    print message
    raise


##
# classes
#


class SessionTiming(Session):
    """ Classe d'une session
    """
    def __unicode__(self):
        return super(SessionTiming, self).__unicode__(session_timing_body_template, session_timing_header_template)


class SessionPresentationTiming(SessionPresentation):
    """ Classe d'une présentation
    """

    def __init__(self, *args, **kwargs):
        supervizors = []
        super(SessionPresentationTiming, self).__init__(
                *args,
                supervizors=supervizors,
                **kwargs
                )

    def __unicode__(self):
        presentation_orig = super(SessionPresentationTiming, self).__unicode__(session_timing_item_template)
        presentation_template = Template(presentation_orig)
        presentation_str = presentation_template.substitute(
                duration=unicode(self.duration).split(':')[1] + '~min'
                )
        return presentation_str

