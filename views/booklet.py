#-*- coding: utf8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import
import logging
import os
from ..utils import utils
from .jdd import BasicView, TEMPLATE_DIRECTORY


SECTION_TEMPLATE = 'section.tex_template'
SECTION_PATTERN = 'section_{}.tex'
BOOKLET_TEMPLATE = 'booklet.tex_template'
BOOKLET_PATTERN = 'booklet.tex.sample'
DIRECTORY_PICTURES = 'pictures'


class BookletView(BasicView):
    """Vue pour la génération d'un fichier LaTeX contenant le recueil des
    résumés courts.

    La vue récupère les données stockées par les modèles et mises en ordre par
    le contrôleur. Elle utilise Jinja2 pour le moteur de template.

    Le livret se divise en un fichier principal `BOOKLET` et une série de
    fichiers pour chaque section `SECTION`. Ceci évite d'avoir un seul fichier
    de recueil qui serait très gros et pas pratique pour les modifications à la
    dernière minute.

    Attributes:
        logger (:obj:`logging.Logger`): logger pour toute la classe.
        environment (:obj:`jinja2.environment.Environment`): enviornnement de
            templates pour Jinja2. Il a été adapté pour que la syntaxe coïncide
            avec LaTeX. Les accolades LaTeX faisaient interférence avec les
            accolades du langage de template par défaut.
        section_template_loaded (bool): flag pour indiquer si le template de
            la section a été chargé par Jinja2.
        booklet_template_loaded (bool): flag pour indiquer si le template du
            recueil a été chargé par Jinja2.
    """
    logger = logging.getLogger('views.booklet.BookletView')

    def __init__(self):
        self.section_template_loaded = False
        self.booklet_template_loaded = False

    def retrieve(self, sections):
        """Formate les sections du recueil dans le template.

        Args:
            sections (:obj:`list` of :obj:`Section`): liste des sections.

        Returns:
            :obj:`list` of :obj:`dict`: liste de dictionnaires contenant le nom
            des fichiers et leur contenu pour le recueil.

        """
        # la liste des fichiers à écrire, c'est-à-dire le fichier du recueil et
        # les fichiers de section
        files_content = []

        # Jinja2 n'accepte que des dictionnaires en entrée, on va devoir tout
        # convertir
        sections_dict = []

        # parcourir chaque section
        for section in sections:
            # convertir en dictionnaire
            section_dict = utils.todict(section)
            sections_dict.append(section_dict)

            # demender un rendu
            section_content = self._retrieve_section(section_dict)
            section_dict['file_name'] = section_content['file_name']
            files_content.append(section_content)

        # rendre le fichier de recueil
        files_content.append(self._retrieve_booklet(sections_dict))

        return files_content

    def _retrieve_section(self, section_dict):
        """Formate une section dans le template.

        Args:
            section_dict (:obj:`dict`): section sous forme de dictionnaire.

        Returns:
            :obj:`dict`: dictionnaire contenant le nom de fichier à créer et le
            contenu texte.

        """
        # charger le template
        if not self.section_template_loaded:
            self.logger.debug("Charge le template \"{template}\"".format(
                template=os.path.join(
                    TEMPLATE_DIRECTORY,
                    SECTION_TEMPLATE
                    )
                ))

        template = self.environment.get_template(SECTION_TEMPLATE)
        self.section_template_loaded = True

        # ajouter le dossier des photos
        section_dict['directory_pictures'] = DIRECTORY_PICTURES

        # rendre la section
        text = template.render(section_dict)
        file_name = SECTION_PATTERN.format(section_dict['number'])
        self.logger.debug("Génère le texte pour la section \
\"{section}\"".format(section=section_dict['number']))

        return {
                'file_name': file_name,
                'text': text,
                }

    def _retrieve_booklet(self, sections_dict):
        """Formate le fichier principal du recueil.

        Args:
            sections_dict (:obj:`list` of :obj:`dict`): liste des sections sous
                forme de dictionnaire.

        Returns:
            :obj:`dict`: dictionnaire du nom de fichier et du texte du fichier
            principal du recueil.

        """
        # charger le template
        if not self.booklet_template_loaded:
            self.logger.debug("Charge le template \"{template}\"".format(
                template=os.path.join(
                    TEMPLATE_DIRECTORY,
                    BOOKLET_TEMPLATE
                    )
                ))

        template = self.environment.get_template(BOOKLET_TEMPLATE)
        self.booklet_template_loaded = True

        # rendre le recueil
        text = template.render({'sections': sections_dict})
        file_name = BOOKLET_PATTERN
        self.logger.debug("Génère le texte pour le recueil de résumés courts")

        return {
                'file_name': file_name,
                'text': text,
                }
