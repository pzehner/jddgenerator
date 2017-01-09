#-*- coding: utf8 -*-

""" Classe pour la génération du recueil de résumés courts des JDD
"""


##
# imports
#


from __future__ import unicode_literals
from codecs import open
from string import Template
import os
from jdd import Student, PhD, Supervizor

package_path = os.path.dirname(os.path.realpath(__file__))


##
# constantes
#


ABSTRACT_BOOKLET_DIRECTORY = "abstracts_booklet_files"
ABSTRACT_BOOKLET_BODY_FILE = "abstracts_booklet_body.tex"
ABSTRACT_BOOKLET_HEADER_FILE = "abstracts_booklet_header.tex"
ABSTRACT_BOOKLET_SEPARATOR_FILE = "abstracts_booklet_separator.tex"
ABSTRACT_BOOKLET_FILE = "abstracts_booklet.tex"
DEFAULT_PICTURE = "akemi_homura.jpg"


##
# charge les templates
#


def load_template(template_file):
    template_file_path = os.path.join(package_path, ABSTRACT_BOOKLET_DIRECTORY, template_file)
    with open(template_file_path, 'r', encoding='utf8') as file:
        return file.read()

try:
    abstract_booklet_body_template = Template(load_template(ABSTRACT_BOOKLET_BODY_FILE))
    abstract_booklet_header_template = Template(load_template(ABSTRACT_BOOKLET_HEADER_FILE))
    abstract_booklet_separator = load_template(ABSTRACT_BOOKLET_SEPARATOR_FILE)
    abstract_booklet_template = Template(load_template(ABSTRACT_BOOKLET_FILE))
except Exception:
    message = "Erreur à l'ouverture des fichiers de template"
    print message
    raise


##
# paramètres
#


##
# classes
#


class Booklet:
    """ Classe pour un ensemble de résumés courts
    """

    def __init__(self, abstracts):
        # stocke les abstracts si ce sont des BookletAbstracts
        # ou les converti à la volée
        if abstracts and type(abstracts) in (list, tuple):
            abstract0 = abstracts[0]
            if type(abstract0) in (tuple, list):
                self.abstracts = [BookletAbstract(*a) for a in abstracts]
            elif isinstance(abstract0, BookletAbstract):
                self.abstracts = abstracts
            else:
                raise ValueError("Valeur d'entrée invalide : abstract, " + \
                        unicode(type(abstract0)))
            self.abstracts.sort(key=lambda e: e.order)
        else:
            self.abstracts = []

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        first = True
        document_str = ""
        for abstract in self.abstracts:
            document_str += abstract_booklet_separator if not first else ""
            document_str += unicode(abstract)
            first = False
        return document_str


class BookletAbstract:
    """ Classe pour un résumé court
    """

    def __init__(self, code, title, presentator, grade, department, \
            unit, location, email, picture, supervizors, directors, funding, \
            keywords=[], abstract="", color="", order=0):
        self.code = code
        self.student = Student(
                name=presentator,
                grade=grade,
                department=department,
                unit=unit,
                location=location,
                email=email,
                picture=picture
                )
        self.phd = PhD(
                title=title,
                funding=funding,
                supervizors=supervizors,
                directors=directors
                )

        self.abstract = abstract
        if type(keywords) not in (list, tuple):
            keywords = [keywords]
        self.keywords = keywords
        self.order = order
        self.color = color

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        # header
        header_str = abstract_booklet_header_template.substitute(
                color=self.color,
                name=self.student.name,
                department_unit=self.student.department + '/' + self.student.unit \
                        if self.student.unit else self.student.department,
                grade=self.student.grade,
                picture=self.student.picture or DEFAULT_PICTURE,
                email=self.student.email,
                location=self.student.location,
                funding=self.phd.funding,
                supervizors=' \\par '.join([unicode(s).replace('(', '\\allowbreak (') for s in self.phd.supervizors]),
                directors=' \\par '.join([unicode(d).replace('(', '\\allowbreak (') for d in self.phd.directors]),
                supervizor_plural='s' if len(self.phd.supervizors) - 1 else '',
                director_plural='s' if len(self.phd.directors) - 1 else ''
                )
        body_str = abstract_booklet_body_template.substitute(
                title=self.phd.title,
                keywords=', '.join(self.keywords),
                abstract=self.abstract
                )
        document_str = abstract_booklet_template.substitute(
                header=header_str,
                body=body_str
                )
        return document_str
