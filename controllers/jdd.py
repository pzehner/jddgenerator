#-*- coding: utf8 -*-
from __future__ import unicode_literals
import logging
import os
from codecs import open
from ..views.jdd import JddView
from ..utils.csv_dict import CSVDict
from ..config import config
from ..models.jdd import Student, PhD, Supervizor, Director


class BasicController(object):
    """Contrôleur générique utilisé comme base pour les autres contrôleurs du
    projet.

    Ce contrôleur n'a pas pour but d'être instancié. La méthode `write`
    permet d'écrire des données sur le disque. Typiquement, il s'agit des
    données générées par la méthode `retrieve` définie dans les classes
    filles.

    Attributes:
        logger (:obj:`logging.Logger`): logger pour toute la classe.

    """
    logger = logging.getLogger('controllers.jdd.BasicController')

    def get_phds(self, students_file):
        """Récupère les thèses depuis la liste des doctorants.

        Cette méthode est utilisée pour la génération du listing et du recueil
        des résumés courts, elle a donc été mutualisée dans la plus proche
        classe parente de `PlanningController` et de `BookletController`.

        Args:
            students_file (unicode): fichier de configuration pour charger la
                liste CSV des doctorants, qui doit contenir les sujets, les
                doctorants et les encadrants.

        Returns:
            :obj:`list` of tuple: {
                unicode: code du doctorant, son identifiant unique utilisé à
                    d'autres endroits.
                bool: `True` si le doctorant est présent aux JDD, `False`
                    suivant.
                :obj:`PhD`: thèse, contenant le doctorant, le sujet, les
                    encadrants et les directeurs.
            }

        """
        # lire le fichier CSV
        students = CSVDict()
        students.read(students_file)

        # créer les objets
        phds = []

        # lire chaque ligne
        # On lit les lignes du fichier qui liste les doctorants avec leur sujet
        # et leur encadrants/directeurs. On considère que chaque ligne donne
        # une présentation.
        for line in students:
            # flag pour indiquer si la thèse sera présentée
            come_flag = config.getboolean('booleans', line['come'].lower())

            # code
            code = line['code']

            # doctorant
            student = Student(
                    name=(
                        line['first-name'] + ' ' + line['name']
                        ).title(),

                    grade=line['grade'],
                    department=line['department'],
                    unit=line['unit'],
                    location=line['location'],
                    picture=code,
                    email=line['email']
                    )

            # encadrants
            # On charge tous les encadrants possibles. Comme on ne connait pas
            # leur nombre, on utilise une boucle infinie. Ceci marche car les
            # champs concernant les encadrants dans le fichier de configuration
            # sont préfixés du numéro d'encadrant : `s1-name` avec `s` pour
            # "supervizor".
            supervizors = []
            i = 0
            while True:
                # On vérifie que le nom de l'encadrant suivant existe et
                # n'est pas vide.
                # TODO commencer à 0
                i += 1
                if "s{}-name".format(i) not in line or \
                        not line["s{}-name".format(i)]:
                            break

                # dans ce cas ajouter l'encadrant
                prefix = 's{}-'.format(i)
                supervizors.append(Supervizor(
                    title=line[prefix + 'title'],
                    name=line[prefix + 'name'].title(),
                    origin=line[prefix + 'origin'],
                    department=line[prefix + 'department'],
                    unit=line[prefix + 'unit']
                    ))

            # directeurs
            # Même logique que pour les encadrants.  Sauf que les champs
            # concernant les directeurs sont préfixés par `d`, pour "director" :
            # `d1-name`.
            directors = []
            i = 0
            while True:
                # On vérifie que le nom du directeur suivant existe et n'est
                # pas vide.
                i += 1
                if "d{}-name".format(i) not in line or \
                        not line["d{}-name".format(i)]:
                            break

                # dans ce cas ajouter le directeur
                prefix = 'd{}-'.format(i)
                directors.append(Director(
                    title=line[prefix + 'title'],
                    name=line[prefix + 'name'].title(),
                    origin=line[prefix + 'origin']
                    ))

            # thèse
            phd = PhD(
                    title=line['title'],
                    funding=line['funding'],
                    )

            # logger la ligne
            self.logger.debug("Extrait la ligne \"{code}\": \"{phd}\"{come}".format(
                code=code,
                phd=phd,
                come="" if come_flag else " (absent)"
                ))

            # faire les liens entre les objets
            phd.set_student(student)
            phd.add_supervizors(supervizors)
            phd.add_directors(directors)

            # ajouter la thèse ainsi que son code et son flag de présentation
            phds.append((code, come_flag, phd))

        return phds

    def write(self, text, directory):
        """Écrit une liste de données formatées dans un fichier texte.

        Args:
            text (:obj:`dict`): dictionnaire contenant le non de
                fichier et le contenu texte.
            directory (unicode): dossier où enregistrer les fichiers.

        """
        if isinstance(text, list):
            # écrire les fichiers
            for text_item in text:
                self.write(text_item, directory)

            return

        # créer le dossier de sortie
        if not os.path.isdir(directory):
            os.makedirs(directory)

        # préparer le nom du fichier
        file_name = text['file_name']
        file_path = os.path.join(directory, file_name)

        # écrire
        with open(file_path, 'w', encoding='utf8') as file:
            file.write(text['text'])
            self.logger.info("Écris le fichier \"{file}\"".format(
                file=file_path
                ))

    def _write_texts(self, texts, directory):
        """Écrit une liste de données formatées dans un fichier texte.

        Args:
            texts (:obj:`list` of :obj:`dict`): liste de dictionnaires
                contenant le non de fichier et le contenu texte.
            directory (unicode): dossier où enregistrer les fichiers.

        """
        # écrire les fichiers
        for text in texts:
            self._write_text(text, directory)


class JddController(BasicController):
    """Contrôleur pour la génération du fichier principal.

    Le contrôleur donne accès aux méthodes pour la génération du fichier
    principal. La méthode `retrieve` crée le fichier principal dans le
    dossier de sortie.

    Attributes:
        logger (:obj:`logging.Logger`): logger pour toute la classe.

    """
    logger = logging.getLogger('controllers.jdd.JddController')

    def retrieve(self, directory):
        """Donne une représentation des sessions en passant par la vue.

        Args:
            directory (unicode): dossier de sortie où enregistrer les
                fichiers.

        """
        # créer une vue et récupérer le document
        view = JddView()
        main = view.retrieve()

        # écrire le résulat
        self.write(main, directory)
