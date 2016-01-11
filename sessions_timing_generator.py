#-*- coding: utf8 -*-


##
# imports
#


from __future__ import unicode_literals
from csv_unicode import unicode_csv_reader
from session_timing import SessionTiming, SessionPresentationTiming
from codecs import open
import datetime
import os
from sessions_generator import SessionsJob


##
# paramètres
#


##
# classe
#


class SessionsTimingJob(SessionsJob):
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
                    listing.append(SessionPresentationTiming(
                        code=line[li['code']],
                        title=line[li['title']],
                        presentator=line[li['first_name']] + ' ' + line[li['name']].title(),
                        grade=line[li['grade']],
                        department=line[li['department']],
                        unit=line[li['unit']],
                        ))
        self.presentations = listing

    def make_sessions(self, *args, **kwargs):
        super(SessionsTimingJob, self).make_sessions(*args, session_class=SessionTiming, **kwargs)


##
# script
#


def make_sessions_timing(
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

    sessions_timing_job = SessionsTimingJob(
            listing_file,
            listing_index,
            **pick_extra('listing_file_skip_lines')
            )
    sessions_timing_job.add_timings(
            timings_file,
            timings_index,
            **pick_extra('timings_file_skip_lines')
            )
    sessions_timing_job.make_sessions(
            sessions_names,
            sessions_colors,
            sessions_days,
            sessions_timings,
            sessions_presentators
            )
    sessions_timing_job.write_output(
            out_directory
            )
