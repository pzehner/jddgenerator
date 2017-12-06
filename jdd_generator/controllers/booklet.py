#-*- coding: utf8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

import os
import sys
import logging
from glob import glob
from colour import Color

from ..utils import utils
from ..utils.csv_dict import CSVDict
from ..models.booklet import Section, Abstract
from .jdd import BasicController, OUTPUT_DIRECTORY
from .planning import STUDENTS_FILE, REPARTITIONS_FILE
from ..views.booklet import BookletView, PICTURES_TARGET_DIRECTORY


BOOKLET_FILE = 'booklet.ini'
ABSTRACT_FILES = 'abstracts.ini'
PICTURES_DIRECTORY = 'photos'


class BookletController(BasicController):
    """Contrôleur pour la génération des fichiers du recueil de résumés courts.

    Le contrôleur donne accès aux méthodes pour la génération des fichiers du
    recueil de résumés courts. La méthode `create` récupère les données des
    fichiers d'entrée, puis les ordonne avec les classes des modèles. La méthode
    `retrieve` envoit ces données à la vue pour les formatter en fichiers LaTeX.
    Le résultat est ensuite écrit sur le disque.

    Attributes:
        logger (:obj:`logging.Logger`): logger pour toute la classe.
        abstracts (:obj:`list` of :obj:`Abstract`): liste des résumés (n'a pas
            vraiment de sens en tant qu'attribut, mais ça permet de faciliter le
            passage de cette variable).
        sections (:obj:`list` of :obj:`Section`): liste des sections du recueil.
        directory_pictures (unicode): dossier source pour les photos.
    """
    logger = logging.getLogger('controllers.booklet.BookletController')

    def __init__(self):
        self.abstracts = []
        self.sections = []
        self.directory_pictures = ''

    def create(self, booklet_file=BOOKLET_FILE, abstracts_file=ABSTRACT_FILES,
            students_file=STUDENTS_FILE, repartitions_file=REPARTITIONS_FILE,
            directory_pictures=PICTURES_DIRECTORY):
        """Crée la structure de données pour le recueil depuis les différents
        fichiers d'entrée.

        Args:
            booklet_file (unicode): fichier de configuration pour charger le
                listing CSV des sections du recueil.
            abstracts_file (unicode): fichier de configuration pour charger le
                listing CSV des résumés.
            students_file (unicode): fichier de configuration pour charger le
                listing CSV des doctorants, des thèses, des encadrantse et des
                directeurs.
            repartitions_file (unicode): fichier de configuration pour charger
                le listing CVS des timings, qui contient l'affectation de chaque
                résumé dans les sections.
            directory_pictures (unicode): chemin vers le dossier source des
                photos.
        """
        # vérifier le dossier source pour les photos
        self._set_directory_pictures(directory_pictures)

        # créer les sections
        self._create_sections(booklet_file)

        # créer les résumés
        self._create_abstracts(abstracts_file)

        # ajouter les thèses aux résumés
        self._apply_phds(students_file)

        # ajouter l'ordre des thèses depuis le fichier des répartitions pour les
        # présentations
        self._apply_repartitions(repartitions_file)

        # ordonner les sections
        self._sort_sections()

        # ordonner et répartir les résumés
        self._sort_abstracts()

    def retrieve(self, directory=OUTPUT_DIRECTORY):
        """Donne une représentation du recueil de résumés en passant par la vue.

        Appelle la vue pour convertir les données en LaTeX, puis écris le
        résultat sur le disque et crée l'arborescence.

        Args:
            directory (unicode): dossier de sortie où enregistrer les fichiers.

        """
        # on crée une vue et on lui passe les données
        view = BookletView()
        files_content = view.retrieve(self.sections)

        # dossier pour écrire les fichiers du recuiel de résumés courts
        directory_booklet = os.path.join(directory, 'booklet')

        # écrire
        self._write(files_content, directory_booklet)

        # créer le lien du dossier de photos
        self._create_directory_picture_link(directory_booklet)

    def _set_directory_pictures(self, directory_pictures):
        """Vérifier le dossier des photos.

        Args:
            directory_pictures (unicode): chemin vers le dossier source des
                photos.

        """
        # on vérifie que le dossier existe
        if not os.path.isdir(directory_pictures):
            raise ValueError("Le dossier de photos \"{}\" n'est pas \
valide".format(directory_pictures).encode(sys.stderr.encoding))

        # on le charge
        self.directory_pictures = directory_pictures

    def _create_sections(self, booklet_file):
        """Extraire les données du fichier de configuration du recueil.

        Args:
            booklet_file (unicode): fichier de configuration pour charger le
                listing CSV des sections du recueil.
        """
        # lire le fichier CSV
        sections = CSVDict()
        sections.read(booklet_file)

        # parcourir toutes les sections
        for section in sections:
            # on extrait des paramètres en avance pour les traiter
            # gestion de la couleur
            color_mode = section['color-mode']
            color_value = section['color']
            if color_value.startswith('#'):
                color = Color(color_value)

            else:
                color_dict = {color_mode: utils.read_tuple(color_value)}
                color = Color(**color_dict)

            # on crée la section
            section_obj = Section(
                    number=int(section['number']),
                    color=color
                    )

            self.sections.append(section_obj)
            self.logger.debug("Ajoute la \"{section}\" au recueil".format(
                section=section_obj
                ))

    def _create_abstracts(self, abstracts_file):
        """Extraire les données des résumés.

        Args:
            abstracts_file (unicode): fichier de configuration pour charger le
                listing CSV des résumés.
        """
        # ouvrir le fichier CSV
        abstracts = CSVDict()
        abstracts.read(abstracts_file)

        # initialiser les résumés
        # On stocke les résumés dans l'instance de la classe parce que ça
        # simplifie leur accès.
        self.abstracts = []

        # on parcours chaque résumé
        for abstract in abstracts:
            code = abstract['code']

            # test de validité
            # Si le résumé n'a pas de contenu (le texte du résumé lui-même), on
            # logge et on continue.
            if not abstract['text']:
                self.logger.warning("La ligne \"{}\" n'a pas de résumé".format(
                    code
                    ))

                continue

            # TODO nettoyer la ligne des caractères exotiques
            text = abstract['text']

            # on récupère les mots clés et on en fait une liste
            keywords = [l.strip() for l in \
                    abstract['keywords'].replace(';', ',').split(',')]

            # on crée et sauvegarde l'objet
            abstract_obj = Abstract(
                    code=code,
                    text=text,
                    keywords=keywords
                    )

            self.abstracts.append(abstract_obj)

            self.logger.debug("Ajoute le résumé \"{abstract}\" au \
contrôleur".format(abstract=abstract_obj))

    def _apply_phds(self, students_file):
        """Ajouter les thèses

        Args:
            students_file (unicode): fichier de configuration pour charger le
                listing CSV des doctorants, des thèses, des encadrants et des
                directeurs.
        """
        # on récupère les thèses par la méthode générique
        phds = self._get_phds(students_file)

        # lister tous les sujets
        for code, come_flag, phd in phds:
            # si la thèse n'est pas présentée, on continue sans logger
            if not come_flag:
                continue

            # on récupère le résumé correspondant par le code
            abstract = self._get_abstract_by_code(code)

            # Si aucun résumé ne correspond au code, logger l'erreur et
            # continuer.
            if abstract is None:
                self.logger.warning("La ligne des doctorants \
\"{code}\" ne correspond à aucun résumé".format(
                    code=code
                    ))

                continue

            # vérifier qu'une photo existe
            path_picture = os.path.join(self.directory_pictures, code)
            if not glob(path_picture + '.*'):
                self.logger.warning("Le doctorant \"{student}\" n'a pas de \
photo".format(student=phd.student))

                # ne plus faire référence à la photo
                phd.student.picture = ''

            # ajouter la thèse
            abstract.set_phd(phd)

            self.logger.debug("Ajout la thèse \"{phd}\" au résumé \
\"{abstract}\"".format(
                phd=phd,
                abstract=abstract
                ))

    def _apply_repartitions(self, repartitions_file):
        """Extraire les données de répartition.

        On se sert de la répartition des présentations du timing pour répartir
        les résumés.

        Args:
            repartitions_file (unicode): fichier de configuration pour charger
                le listing CVS des timings, qui contient l'affectation de chaque
                résumé dans les sections.
        """
        # lire le fichier CSV
        repartitions = CSVDict()
        repartitions.read(repartitions_file)

        # on parcours chaque timimg
        for repartition in repartitions:
            # on récupère le résumé avec le code
            code = repartition['code']
            abstract = self._get_abstract_by_code(code)

            # Si aucun résumé ne correspond au code, logger l'erreur et
            # continuer.
            if abstract is None:
                self.logger.warning("La ligne de répartiton des timings \
\"{code}\" ne correspond à aucun résumé".format(
                    code=code
                    ))

                continue

            # on récupère les infos qui nous intéressent
            abstract.section = int(repartition['session'])
            abstract.order = int(repartition['order'])

            self.logger.debug("Ajoute les infos de répartition au résumé \
\"{abstract}\"".format(abstract=abstract))

    def _sort_sections(self):
        """Trier les sections

        Les sections sont triées par numéro.

        """
        self.sections.sort(key=lambda s: s.number)

    def _sort_abstracts(self):
        """Affecter les présentations aux sections et les trier.

        """
        # on parcours les sections
        for section in self.sections:
            # on récupère les résumés qui sont associés à cette section
            abstracts = self._get_abstracts_by_section_number(section.number)
            abstracts.sort(key=lambda a: a.order)

            # on ajoute l'info de couleur et on affecte le résumé à la section
            for abstract in abstracts:
                abstract.color = section.color
                section.add_abstract(abstract)

    def _get_abstracts_by_section_number(self, number):
        """Retourne une liste de résumés de la même section.

        Args:
            number (int): numéro de section.

        Returns:
            :obj:`list` of :obj:`Abstract`: liste de résumés associées à cette
            section.

        """
        return [a for a in self.abstracts if a.section == number]

    def _get_abstract_by_code(self, code):
        """Retourne un résumé par son code.

        Args:
            code (str): code unique du résumé.

        Returns:
            :obj:`Abstract`: résumé correspondant.

        """
        for abstract in self.abstracts:
            if abstract.code == code:
                return abstract

        return None

    def _create_directory_picture_link(self, directory_booklet):
        """Fait le lien du dossier de photos dans le dossier de sortie.

        Args:
            directory_booklet (unicode): dossier où le recueil est écrit.
        """
        directory_pictures_target = os.path.join(directory_booklet,
                PICTURES_TARGET_DIRECTORY)

        # si le chemin était absolu, `join` ne prend pas en compte le premier
        # arguement
        directory_pictures_source = os.path.join(os.getcwd(),
                self.directory_pictures)

        # on fait le lien que si le dossien n'existe pas
        if not os.path.isdir(directory_pictures_target):
            os.symlink(
                    directory_pictures_source,
                    directory_pictures_target
                    )

            self.logger.debug("Création du lien du dossier de photos \
\"{source}\" vers \"{target}\"".format(
                    source=directory_pictures_source,
                    target=directory_pictures_target
                    ))

        else:
            self.logger.debug("Le dossier de photos \"{}\" est déjà \
présent".format(directory_pictures_target))
