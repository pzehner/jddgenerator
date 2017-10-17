#-*- coding: utf8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

import os
from codecs import open

from ConfigParser import SafeConfigParser


CONFIG_FILE_NAME = 'config.ini'


# préparer le chemin du fichier de config
_jdd_generator_path = os.path.dirname(os.path.abspath(__file__))
_config_file_path = os.path.join(_jdd_generator_path, CONFIG_FILE_NAME)


# vérifier que le fichier existe
if not os.path.isfile(_config_file_path):
    message = "Le fichier de configuration 'config.ini' n'a pas été trouvé"
    raise IOError(message)


# charger la config
config = SafeConfigParser()
with open(_config_file_path, 'r', encoding='utf8') as file:
    config.readfp(file)
