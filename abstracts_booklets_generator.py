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


##
# classe
#


class AbstractsBookletJob:
    """ Classe décrivant un travail de création de livret de résumés
    """

    def __init__(self, listing_file, listing_index, pictures_path,
            picture_default, listing_file_skip_lines=1):
        li = listing_index
        with open(listing_file, 'r', encoding='utf-8') as file:
            listing_csv = unicode_csv_reader(file, delimiter=b'\t')

            listing = []
            for line in list(listing_csv)[listing_file_skip_lines:]:
                if line[li['come']].lower() != "non":
                    picture = os.path.join(pictures_path, line[li['code']])
                    picture_avail = glob.glob(picture + '*')
                    picture_path = picture_avail[0] if len(picture_avail) else picture_default
                    listing.append(BookletAbstract(
                        code=line[li['code']],
                        title=line[li['title']],
                        presentator=line[li['first_name']] + ' ' + line[li['name']].title(),
                        grade=line[li['grade']],
                        department=line[li['department']],
                        unit=line[li['unit']],
                        location=line[li['location']],
                        email=line[li['email']],
                        picture=picture_path,
                        supervizors=[
                            (
                                line[li['s1_title']],
                                line[li['s1_name']],
                                line[li['s1_origin']],
                                line[li['s1_department']],
                                line[li['s1_unit']],
                                ),
                            (
                                line[li['s2_title']],
                                line[li['s2_name']],
                                line[li['s2_origin']],
                                line[li['s2_department']],
                                line[li['s2_unit']],
                                ),
                            (
                                line[li['s3_title']],
                                line[li['s3_name']],
                                line[li['s3_origin']],
                                line[li['s3_department']],
                                line[li['s3_unit']],
                                ),
                            ],
                        directors=[
                            (
                                line[li['d1_title']],
                                line[li['d1_name']],
                                line[li['d1_origin']],
                                ),
                            (
                                line[li['d2_title']],
                                line[li['d2_name']],
                                line[li['d2_origin']],
                                ),
                            ],
                        funding=line[li['funding']]
                        ))
        self.listing = listing

    def add_timings(self, timings_file, timings_index, timings_file_skip_lines=1):
        """ Ajoute les informations de passage depuis un fichier CSV
        """
        ti = timings_index
        with open(timings_file, 'r', encoding='utf-8') as file:
            timings_csv = unicode_csv_reader(file, delimiter=b'\t')

            for line in list(timings_csv)[timings_file_skip_lines:]:
                code = line[ti['code']]
                if int(line[ti['day']]):
                    listing_match = [l for l in self.listing if l.code == code]
                    if listing_match:
                        listing_current = listing_match[0]
                        listing_current.session = int(line[ti['session']])
                        listing_current.order = int(line[ti['order']])
                else:
                    print "ligne orpheline :", code

    def add_abstracts(self, abstracts_file, abstracts_index, abstracts_file_skip_lines=1):
        """ Ajoute les résumés et les mots clés depuis un fichier CSV
        """
        ai = abstracts_index
        with open(abstracts_file, 'r', encoding='utf-8') as file:
            abstracts_csv = unicode_csv_reader(file, delimiter=b'\t')

            for line in list(abstracts_csv)[abstracts_file_skip_lines:]:
                code = line[ai['code']]
                if line[ai['abstract']]:
                    listing_match = [l for l in self.listing if l.code == code]
                    if listing_match:
                        listing_curent = listing_match[0]
                        listing_curent.abstract = line[ai['abstract']]
                        listing_curent.keywords = [l.strip() for l in line[ai['keywords']].replace(';', ',').split(',')]
                else:
                    print "ligne orpheline :", code

    def make_booklets(self, sessions_colors):
        """ Crée les livrets
        """
        for abstract in self.listing:
            abstract.color = sessions_colors[abstract.session - 1]

        # répartition en sessions
        self.listing.sort(key=lambda e: (e.session, e.order))
        sessions = itertools.groupby(self.listing, key=lambda e: e.session)

        # création des livrets
        booklets = []
        for session, group in sessions:
            booklets.append(Booklet(abstracts=list(group)))

        self.booklets = booklets

    def write_output(self, out_directory):
        """ Écrire les résultats
        """
        out_file_pattern = 'abstracts_{0}.tex'
        if not os.path.isdir(out_directory):
            os.mkdir(out_directory)
        for i, booklet in enumerate(self.booklets):
            out_file_name = out_file_pattern.format(i + 1)
            out_file_path = os.path.join(out_directory, out_file_name)
            with open(out_file_path, 'w', encoding='utf8') as file:
                file.write(unicode(booklet))


##
# script
#


def make_abstracts_booklets(
        listing_file,
        listing_index,
        picture_path,
        picture_default,
        timings_file,
        timings_index,
        abstracts_file,
        abstracts_index,
        sessions_colors,
        out_directory,
        **kwargs
        ):
    """ Générateur
    """
    def pick_extra(key):
        return {key: kwargs[key]} if key in kwargs else {}

    abstracts_booklets_job = AbstractsBookletJob(
            listing_file,
            listing_index,
            picture_path,
            picture_default,
            **pick_extra('listing_file_skip_lines')
            )
    abstracts_booklets_job.add_timings(
            timings_file,
            timings_index,
            **pick_extra('timings_file_skip_lines')
            )
    abstracts_booklets_job.add_abstracts(
            abstracts_file,
            abstracts_index,
            **pick_extra('abstracts_file_skip_lines')
            )
    abstracts_booklets_job.make_booklets(
            sessions_colors,
            )
    abstracts_booklets_job.write_output(
            out_directory
            )
