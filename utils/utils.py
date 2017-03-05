#-*- coding: utf8 -*-
"""Outils

Module regroupant les diverses fonctions utiles au projet. Ces outils sont
utilisés dans plusieurs fichiers et ont été regroupés ici pour faciliter leur
accès.

"""


from __future__ import unicode_literals
import locale
from datetime import datetime
from colour import Color


locale.setlocale(locale.LC_ALL, ('fr_FR', 'utf8'))


def read_tuple(string, kind=float):
    """Convertir un string en tuple.

    Parse un string contenant une série de valeurs séparées par des virgules en
    tuple. Le type de données du tuple dépent du paramètre `kind`.

    Args:
        string (unicode): string des valeurs.
        kind (:obj:`type`): type de valeur attendue.

    Return:
        :obj:`generator`: tuple des valeurs parsées

    """
    return (kind(v) for v in string.split(','))


def todict(obj):
    """Transforme un objet en dictionnaire de façon récursive.

    Args:
        obj (:obj:): objet à convertir.

    Returns:
        :obj:`dict`: objet sous forme de dictionnaire.
    """
    data = {}
    if isinstance(obj, (datetime, Color)):
        return obj

    for key, value in obj.__dict__.iteritems():
        try:
            data[key] = todict(value)

        except AttributeError:
            data[key] = value

    return data


def format_time(value):
    """Formate un objet `datetime` en texte ne contenant que le temps.

    Le temps est affiché selon le format "HH:MM".

    Args:
        value (:obj:`datetime`): date source.

    Returns:
        unicode: temps formaté.

    """
    return value.strftime('%H:%M')


def format_date(value):
    """Formate un objet `datetime` en texte ne contenant que la date.

    La date est affichée selon le format "Jour JJ Mois".

    Args:
        value (:obj:`datetime`): date source.

    Returns:
        unicode: date formatée.

    """
    return value.strftime('%A %d %B')


def format_color(value):
    """Formate un objet `Color` en représentation RVB décimale.

    Args:
        value (:obj:`Color`): couleur source.

    Returns:
        unicode: couleur RVB décimale, chaque canal séparé par une virgule.
    """
    return ','.join(str(c) for c in value.rgb)

def format_printable(value):
    """Ne garde que les caractères imprimables d'une chaîne

    Procède en supprimant les caractères ayant un code inférieur à 31 qui
    correspondent à des caractères de contrôles invisibles.

    Args:
        value (unicode): chaîne source.

    Returns:
        unicode: chaîne nettoyée des caractères invisibles.
    """
    control_map = dict.fromkeys(range(32))
    return value.translate(control_map)
