#-*- coding: utf8 -*-


##
# imports
#


from __future__ import unicode_literals
from csv_unicode import unicode_csv_reader
from session import Session, SessionPresentation
from codecs import open
import datetime
import os


##
# paramètres
#


##
# classe
#


class SessionsJob(object):
    """ Classe décrivant un travail de création des sessions
    """

    def __init__(self, listing_file, listing_index, listing_file_skip_lines=1):
        li = listing_index
        with open(listing_file, 'r', encoding='utf-8') as file:
            # listing_csv = csv.reader(file, delimiter=b'\t')
            listing_csv = unicode_csv_reader(file, delimiter=b'\t')

            listing = []
            for line in list(listing_csv)[listing_file_skip_lines:]:
                if line[li['come']].lower() != "non":
                    listing.append(SessionPresentation(
                        code=line[li['code']],
                        title=line[li['title']],
                        presentator=line[li['first_name']] + ' ' + line[li['name']].title(),
                        grade=line[li['grade']],
                        department=line[li['department']],
                        unit=line[li['unit']],
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
                            ]
                        ))
        self.presentations = listing

    def add_timings(self, timings_file, timings_index, timings_file_skip_lines=1):
        """ Ajoute les informations de passage depuis un fichier CSV
        """
        ti = timings_index
        with open(timings_file, 'r', encoding='utf-8') as file:
            timing_csv = unicode_csv_reader(file, delimiter=b'\t')

            for line in list(timing_csv)[timings_file_skip_lines:]:
                code = line[ti['code']]
                if line[ti['day']]:
                    presentation_match = [p for p in self.presentations if p.code == code]
                    if presentation_match:
                        presentation_current = presentation_match[0]
                        presentation_current.duration = datetime.timedelta(minutes=int(line[ti['length']]))
                        presentation_current.day = line[ti['day']]
                        presentation_current.session = int(line[ti['session']])
                        presentation_current.order = int(line[ti['order']])
                else:
                    print "ligne orpheline :", code

    def make_sessions(self, sessions_names, sessions_colors, sessions_days,
            sessions_timings, sessions_presentators, session_class=Session):
        """ Crée les sessions
        """
        sessions_data = zip(
                sessions_names,
                sessions_colors,
                sessions_days,
                sessions_timings,
                sessions_presentators
                )

        sessions = []
        for i, session_data in enumerate(sessions_data):
            session_presentations = [p for p in self.presentations if p.session == i + 1]
            session_presentations.sort(key=lambda e: e.order)
            start = datetime.datetime.combine(session_data[2], session_data[3])
            for presentation in session_presentations:
                presentation.start = start
                start += presentation.duration
                presentation.stop = start
            sessions.append(session_class(
                number=session_data[0],
                color=session_data[1],
                presentator=session_data[4],
                start=datetime.datetime.combine(session_data[2], session_data[3]),
                stop=start,
                day=session_data[2],
                presentations=session_presentations
                ))

        self.sessions = sessions

    def write_output(self, out_directory):
        """ Écrire les résultats
        """
        out_file_pattern = 'session_{0}.tex'
        if not os.path.isdir(out_directory):
            os.mkdir(out_directory)
        for i, session in enumerate(self.sessions):
            out_file_name = out_file_pattern.format(i + 1)
            out_file_path = os.path.join(out_directory, out_file_name)
            with open(out_file_path, 'w', encoding='utf8') as file:
                file.write(unicode(session))


##
# script
#


def make_sessions(
        listing_file,
        listing_index,
        timings_file,
        timings_index,
        sessions_names,
        sessions_colors,
        sessions_days,
        sessions_timings,
        sessions_presentators,
        out_directory,
        **kwargs
        ):
    """ Générateur
    """
    def pick_extra(key):
        return {key: kwargs[key]} if key in kwargs else {}

    sessions_job = SessionsJob(
            listing_file,
            listing_index,
            **pick_extra('listing_file_skip_lines')
            )
    sessions_job.add_timings(
            timings_file,
            timings_index,
            **pick_extra('timings_file_skip_lines')
            )
    sessions_job.make_sessions(
            sessions_names,
            sessions_colors,
            sessions_days,
            sessions_timings,
            sessions_presentators
            )
    sessions_job.write_output(
            out_directory
            )


