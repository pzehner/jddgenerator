#!/usr/bin/env python2
#-*- coding: utf8 -*-


##
# imports
#


from __future__ import unicode_literals
from csv_unicode import unicode_csv_reader
from csv_files import *
from session import Session, SessionPresentation
from codecs import open
import datetime


##
# paramètres
#


##
# script
#


# créer le listing
with open(listing_file, 'r', encoding='utf-8') as file:
    # listing_csv = csv.reader(file, delimiter=b'\t')
    listing_csv = unicode_csv_reader(file, delimiter=b'\t')

    listing = []
    first = True
    for line in listing_csv:
        # sauter la première ligne
        if first:
            first = False
            continue
        if line[L_COME].lower() != "non":
            listing.append(SessionPresentation(
                code=line[L_CODE],
                title=line[L_TITLE],
                presentator=line[L_FIRST_NAME] + ' ' + line[L_NAME].title(),
                grade=line[L_GRADE],
                department=line[L_DEPARTMENT],
                unit=line[L_UNIT],
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
                    ]
                ))

# enrichir les présentations avec les infos de passage
with open(presentations_session_file, 'r', encoding='utf-8') as file:
    presentations_session_csv = unicode_csv_reader(file, delimiter=b'\t')

    first = True
    for line in presentations_session_csv:
        # sauter la première ligne
        if first:
            first = False
            continue
        code = line[S_CODE]
        if line[S_DAY]:
            listing_match = [l for l in listing if l.code == code]
            if listing_match:
                listing_current = listing_match[0]
                listing_current.duration = datetime.timedelta(minutes=int(line[S_LENGTH]))
                listing_current.day = line[S_DAY]
                listing_current.session = int(line[S_SESSION])
                listing_current.order = int(line[S_ORDER])
        else:
            print "ligne orpheline :", code


# création des sessions
day_1 = datetime.date(2016, 1, 19)
day_2 = datetime.date(2016, 1, 20)

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

sessions_data = [
        ('Session 1', colors_str[0], day_1, datetime.time(9, 10), ""),
        ('Session 2', colors_str[1], day_1, datetime.time(10, 40), "Paul Zehner (Onera)"),
        ('Session 3', colors_str[2], day_1, datetime.time(13, 30), "Pierre Brenner (EADS Astrium)"),
        ('Session 4', colors_str[3], day_1, datetime.time(15, 0), "Michel Kern (INRIA)"),
        ('Session 5', colors_str[4], day_2, datetime.time(9, 0), "Alain Forestier (CEA)"),
        ('Session 6', colors_str[5], day_2, datetime.time(10, 45), "Valentin Dupif (Onera)"),
        ('Session 7', colors_str[6], day_2, datetime.time(13, 30), ""),
        ('Session 8', colors_str[7], day_2, datetime.time(15, 0), "Christophe Calvin"),
        ]

sessions = []
for i, session_data in enumerate(sessions_data):
    session_presentations = [l for l in listing if l.session == i + 1]
    session_presentations.sort(key=lambda e: e.order)
    start = datetime.datetime.combine(session_data[2], session_data[3])
    for presentation in session_presentations:
        presentation.start = start
        start += presentation.duration
        presentation.stop = start
    sessions.append(Session(
        number=session_data[0],
        color=session_data[1],
        presentator=session_data[4],
        start=datetime.datetime.combine(session_data[2], session_data[3]),
        stop=start,
        day=session_data[2],
        presentations=session_presentations
        ))


# sortie
out_file_pattern = 'session_{0}.tex'
for i, session in enumerate(sessions):
    out_file_name = out_file_pattern.format(i + 1)
    with open(out_file_name, 'w', encoding='utf8') as file:
        file.write(unicode(session))

