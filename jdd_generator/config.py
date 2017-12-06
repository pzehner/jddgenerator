#-*- coding: utf8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

import os
import sys
import logging
from codecs import open

from ConfigParser import SafeConfigParser


filesystem_encoding = sys.getfilesystemencoding()


CONFIG_FILE_NAME = 'config.ini'


logger = logging.getLogger("config")


# créer une config vide
config = SafeConfigParser()


def set_config(path=None):
    """Charge un fichier de configuration dans le module

    La fonction altère directement l'objet `config` dans le module.

    Args:
        path (unicode): chemin vers le fichier de config.
    """
    # préparer le chemin du fichier de config
    if path is None:
        jdd_generator_path = os.path.dirname(
                os.path.abspath(__file__.decode(filesystem_encoding))
                )

        config_file_path = os.path.join(jdd_generator_path, CONFIG_FILE_NAME)

    else:
        config_file_path = path
        logger.info("Charge le fichier de config \"{}\"".format(config_file_path))

    # vérifier que le fichier existe
    if not os.path.isfile(config_file_path):
        raise IOError("Le fichier de configuration \"{}\" n'a pas été \
trouvé".format(config_file_path).encode(sys.stderr.encoding))

    # charger la config
    with open(config_file_path, 'r', encoding='utf8') as file:
        config.readfp(file)
