#-*- coding: utf8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import
import csv
import os
import string
from ConfigParser import SafeConfigParser
from codecs import open


class CSVDict:
    """Classe permettant de manipuler un fichier CSV comme une liste de
    dictionnaires.

    À la place d'ouvrir le fichier CSV directement, on ouvre un fichier INI
    compagnon qui perment de manipuler le fichier CSV.

    Pour utiliser un objet `CSVDict`, il faut créer une instance de la classe
    puis lui demander de lire ce fichier INI :

    >>> csv_dict = CSVDict() >>> csv_dict.read('my_ini_file.ini')

    Si le fichier est correct et que tout se passe bien, on peut alors pour
    chaque ligne du fichier accéder à une colonne par son nom :

    >>> csv_dict[0]['column_name']

    Ce qui donne la colonne `column_name` de la première ligne (noter que le
    numéro des lignes commence à 0).

    Le fichier compagnon contient deux sections.

    La section `[info]` contient plusieurs paramètres pour ouvrir le fichier
    CSV :
        `file`: chemin vers le fichier CSV. Le chemin est relatif à la position
            du fichier INI.
        `skip`: le nombre de lignes à ignorer au début du fichier CSV. Par
            défaut, la valeur est à 0, c'est-à-dire qu'aucune ligne n'est
            ignorée.
        `delimiter`: le caractère utilisé dans le fichier CSV pour séparer les
            colonnes. Par défaut, il désigne une tabulation.

    La section `[fields]` contient l'assoctiation entre les colonnes et leur
    nom. Pour chaque ligne, la valeur à gauche représente le nom de la colonne
    et la valeur à droite son index. L'index peut être soit sous forme numérique
    en commençant à 0, soit sous forme de lettres, comme dans un tableur (A, B,
    ... AA, AB).

    Par rapport à `csv.DictReader`, l'avantage de cette classe est qu'elle ne
    dépend pas des entêtes du fichier CSV qui pourraient être renommées.  En
    revanche, elle oblige la présence du fichier INI compagnon. En outre, cette
    classe gère directement l'encodage UTF-8 pour les fichiers CSV.

    Attributes:
        skip (int): nombre de lignes à ignorer au début du fichier CSV.
        delimiter (unicode): caractère de séparation entre les colonnes.
        data (list of dict): contenu du fichier CSV parsé. Chaque colonne est
            accessible par le nom de son champ. Ce champ est réinitialisé à
            chaque appel de la méthode `read`.

    """
    def __init__(self):
        self.skip = 0
        self.delimiter = r'\t'
        self.data = []

    def read(self, config_file):
        """Lire un fichier compagnon et par suite son fichier CSV.

        Args:
            config_file (unicode): chemin vers le fichier INI compagnon.

        """
        csv_file, fields = self._read_config(config_file)
        data = self._read_csv(csv_file)
        self._parse(data, fields)

    def _read_config(self, config_file):
        """Lire le fichier INI compagnon.

        Args:
            config_file (unicode): chemin vers le fichier INI compagnon.

        Returns:
            tuple: nom du fichier CSV à ouvrir et liste des champs sous forme de
            tuple clé valeur.

        """
        # vérifier l'existence du fichier de config
        if not os.path.isfile(config_file):
            raise IOError("Impossible de trouver le fichier \
compagnon '{}'".format(config_file))

        # vérifier que le fichier est un fichier INI
        if os.path.splitext(config_file)[1].lower() != '.ini':
            raise ValueError("Le fichier d'entrée doit être un fichier INI")

        # lire la config
        config = SafeConfigParser()
        config.read(config_file)

        # vérifier si le fichier est valide
        if not config.has_section('info'):
            raise ValueError("Le fichier compagnon doit avoir une \
section 'info'")

        if not config.has_section('fields'):
            raise ValueError("Le fichier compagnon doit avoir une \
section 'fields'")

        # récupérer les infos optionnelles
        if config.has_option('info', 'skip'):
            self.skip = config.getint('info', 'skip')

        if config.has_option('info', 'delimiter'):
            self.delimiter = config.get('info', 'delimiter')

        # récupérer le nom du fichier csv
        if not config.has_option('info', 'file'):
            raise ValueError("Le fichier compagnon doit avoir une \
clé 'file' dans la section 'info'")

        # on ajoute le chemin du dossien du fichier compagnon
        file_name = os.path.join(
                os.path.dirname(config_file),
                config.get('info', 'file')
                )

        # récupérer les champs
        fields = config.items('fields')

        return file_name, fields

    def _read_csv(self, csv_file):
        """Lire le fichier CSV de données.

        Args:
            csv_file (unicode): chemin vers le fichier CSV.

        Returns:
            :obj:`list`: liste des données sous forme de list pour chaque ligne.

        """
        # vérifier l'existence du fichier csv
        if not os.path.isfile(csv_file):
            raise IOError("Impossible de trouver le fichier \
CSV '{}'".format(csv_file))

        # lire le fichier csv
        # on utilise le délimiteur adéquat
        # on skippe les premières lignes avec `skip`
        with open(csv_file, 'r', encoding='utf-8') as file:
            return list(
                    unicode_csv_reader(
                        file,
                        delimiter=self.delimiter.decode('string_escape')
                        )
                    )[self.skip:]

    def _parse(self, data, fields):
        """Applique la liste des champs sur les données pour obtenir une liste
        de dictionnaires.

        Args:
            data (list): liste des données sous forme de list pour chaque ligne.
            fields (list): liste des champs sous forme de tuple clé valeur.

        """
        # préparer la liste des index sous forme de chiffres
        indexes = []
        for field, column in fields:
            # on essaie d'extraire directement un chiffre
            try:
                index = int(column)

            # sinon, on converti depuis un index de lettres
            except ValueError:
                index = col2num(column)

            indexes.append((field, index))

        # réinitialiser la valeur
        self.data = []

        # remplir les données
        # chaque ligne est convertie en dictionnaire
        for line in data:
            self.data.append({index[0]: line[index[1]] for index in indexes})

    def __getitem__(self, index):
        return self.data[index]


def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    """Lit un fichier CSV en UTF-8.

    Args:
        unicode_csv_data (file): descripteur de fichier à lire.
        dialect (classjob): type de fichier CSV (je suppose).

    Returns:
        :obj:`iterator`: lignes du fichier CSV décodées depuis UTF-8 vers
        unicode.

    """
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)

    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]


def utf_8_encoder(unicode_csv_data):
    """Renvoit les lignes d'un descripteur de fichier en UTF-8.

    Args:
        unicode_csv_data (file): descripteur du fichier à lire.

    Returns:
        :obj:`iterator`: lignes du fichier encodées en UTF-8.

    """
    for line in unicode_csv_data:
        yield line.encode(b'utf-8')


def col2num(col):
    """Convertit un index de colonne en lettres en index numérique.

    Depuis http://stackoverflow.com/a/12640614 .

    Args:
        col (unicode): index de colonne sous forme de lettres (A, B,... AA, AB).

    Returns:
        int: index de colonne sous forme de chiffre, commence à 0.

    """
    num = 0
    for c in col:
        if c in string.ascii_letters:
            num = num * 26 + (ord(c.upper()) - ord('A')) + 1

    return num - 1
