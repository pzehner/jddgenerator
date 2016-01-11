#!/usr/bin/env python2
#-*- coding: utf8 -*-


##
# imports
#


from __future__ import unicode_literals
from csv_unicode import unicode_csv_reader
from csv_files import *
from abstracts_booklet import Booklet, BookletAbstract
from codecs import open
import itertools
import os
import glob


##
# paramètres
#


pictures_path = "photos/jpg"
default_picture = "akemi_homura.jpg"


##
# script
#


# créer le listing
with open(listing_file, 'r', encoding='utf-8') as file:
    listing_csv = unicode_csv_reader(file, delimiter=b'\t')

    listing = []
    first = True
    for line in listing_csv:
        # sauter la première ligne
        if first:
            first = False
            continue
        if line[L_COME].lower() != "non":
            picture = os.path.join(pictures_path, line[L_CODE])
            picture_avail = glob.glob(picture + '*')
            picture_path = picture_avail[0] if len(picture_avail) else default_picture
            listing.append(BookletAbstract(
                code=line[L_CODE],
                title=line[L_TITLE],
                presentator=line[L_FIRST_NAME] + ' ' + line[L_NAME].title(),
                grade=line[L_GRADE],
                department=line[L_DEPARTMENT],
                unit=line[L_UNIT],
                location=line[L_LOCATION],
                email=line[L_EMAIL],
                picture=picture_path,
                supervizors=[
                    (
                        line[L_S1_TITLE],
                        line[L_S1_NAME],
                        line[L_S1_ORIGIN],
                        line[L_S1_DEPARTMENT],
                        line[L_S1_UNIT],
                        ),
                    (
                        line[L_S2_TITLE],
                        line[L_S2_NAME],
                        line[L_S2_ORIGIN],
                        line[L_S2_DEPARTMENT],
                        line[L_S2_UNIT],
                        ),
                    (
                        line[L_S3_TITLE],
                        line[L_S3_NAME],
                        line[L_S3_ORIGIN],
                        line[L_S3_DEPARTMENT],
                        line[L_S3_UNIT],
                        ),
                    ],
                directors=[
                    (
                        line[L_D1_TITLE],
                        line[L_D1_NAME],
                        line[L_D1_ORIGIN],
                        ),
                    (
                        line[L_D2_TITLE],
                        line[L_D2_NAME],
                        line[L_D2_ORIGIN],
                        ),
                    ],
                funding=line[L_FUNDING]
                ))


# enrichir le listing avec les infos de passage
with open(presentations_session_file, 'r', encoding='utf-8') as file:
    presentations_session_csv = unicode_csv_reader(file, delimiter=b'\t')

    first = True
    for line in presentations_session_csv:
        # sauter la première ligne
        if first:
            first = False
            continue
        code = line[S_CODE]
        if int(line[S_DAY]):
            listing_match = [l for l in listing if l.code == code]
            if listing_match:
                listing_current = listing_match[0]
                listing_current.session = int(line[S_SESSION])
                listing_current.order = int(line[S_ORDER])
        else:
            print "ligne orpheline :", code


# enrichir le listing avec le résumé
with open(abstracts_file, 'r', encoding='utf-8') as file:
    abstracts_csv = unicode_csv_reader(file, delimiter=b'\t')

    first = True
    for line in abstracts_csv:
        # sauter la première ligne
        if first:
            first = False
            continue
        code = line[S_CODE]
        if line[A_ABSTRACT]:
            listing_match = [l for l in listing if l.code == code]
            if listing_match:
                listing_curent = listing_match[0]
                listing_curent.abstract = line[A_ABSTRACT]
                listing_curent.keywords = [l.strip() for l in line[A_KEYWORDS].replace(';', ',').split(',')]
        else:
            print "ligne orpheline :", code


# attribution des couleurs
colors = [
    [ 0.6745098 ,  0.79607843,  0.97647059],
    [ 0.57254902,  0.59215686,  0.81176471],
    [ 0.75294118,  0.84705882,  0.92941176],
    [ 0.6627451 ,  0.8       ,  0.93333333],
    [ 0.8       ,  0.82352941,  0.86666667],
    [ 0.70980392,  0.75686275,  0.8745098 ],
    [ 0.74117647,  0.85490196,  0.8745098 ],
    [ 0.84705882,  0.82745098,  0.85098039]
    ]
colors_str = [','.join([unicode(d) for d in c]) for c in colors]

for abstract in listing:
    abstract.color = colors_str[abstract.session - 1]


# répartition en sessions
listing.sort(key=lambda e: (e.session, e.order))
sessions = itertools.groupby(listing, key=lambda e: e.session)


# création des livrets
booklets = []
for session, group in sessions:
    booklets.append(Booklet(abstracts=list(group)))


# sortie
out_file_pattern = 'abstracts_{0}.tex'
for i, booklet in enumerate(booklets):
    out_file_name = out_file_pattern.format(i + 1)
    with open(out_file_name, 'w', encoding='utf8') as file:
        file.write(unicode(booklet))

