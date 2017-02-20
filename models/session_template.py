import os
import locale
from codecs import open
from string import Template

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


locale.setlocale(locale.LC_ALL, ('fr_FR', 'utf8'))


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


class Session:
    def __str__(self):
        return unicode(self)

    def __unicode__(self, body_template=session_body_template, header_template=session_header_template):
        # header
        header_str = header_template.substitute(
                color=self.color,
                number=self.number,
                start=self.start.strftime(STRF_TIME),
                stop=self.stop.strftime(STRF_TIME),
                chairman=self.chairman
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


class SessionPresentation:
    def __str__(self):
        return unicode(self)

    def __unicode__(self, template=session_item_template):
        presentation_str = template.safe_substitute(
                start=self.start.strftime(STRF_TIME),
                stop=self.stop.strftime(STRF_TIME),
                title=self.phd.title,
                chairman=self.student.name,
                supervizors=', '.join([unicode(s) for s in set(self.phd.supervizors)]),
                grade=self.student.grade,
                origin=self.student.department + '/' + self.student.unit \
                        if self.student.unit else self.student.department
                )
        return presentation_str


class SessionPresentationSupervizor:
    def __unicode__(self):
        string = ""
        string += self.title + '~' if self.title else ''
        string += self.name
        string += ' (\small{' + self.origin + '})' if self.origin else ''
        return string
