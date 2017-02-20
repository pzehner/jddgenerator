#-*- coding: utf8 -*-


##
# imports
#


from __future__ import unicode_literals
import logging
import os
from codecs import open
from ..views.jdd import JddView


class BasicController(object):
    logger = logging.getLogger('controllers.jdd.BasicController')

    def _write_text(self, text, directory):
        """ Écrit une liste de données formatées dans un fichier texte

            Args:
                text (:obj:`dict`): dictionnaire contenant le non de
                    fichier et le contenu texte.
                directory (unicode): dossier où enregistrer les fichiers.
        """
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
        """ Écrit une liste de données formatées dans un fichier texte

            Args:
                texts (:obj:`list` of :obj:`dict`): liste de dictionnaires
                    contenant le non de fichier et le contenu texte.
                directory (unicode): dossier où enregistrer les fichiers.
        """
        # écrire les fichiers
        for text in texts:
            self._write_text(text, directory)


class JddController(BasicController):
    """ Contrôleur pour la génération du fichier principal

        Le contrôleur donne accès aux méthodes pour la génération du fichier
        principal. La méthode `retrieve` crée le fichier principal dans le
        dossier de sortie.

        Attributes:
            logger (:obj:`logging.Logger`): logger pour toute la classe.
    """
    logger = logging.getLogger('controllers.jdd.JddController')

    def retrieve(self, directory):
        """ Donne une représentation des sessions en passant par la vue

            Args:
                directory (unicode): dossier de sortie où enregistrer les
                    fichiers.
        """
        # créer une vue et récupérer le document
        view = JddView()
        main = view.retrieve()

        # écrire le résulat
        self._write_text(main, directory)



