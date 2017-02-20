#-*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from datetime import datetime
from colour import Color



class Event(object):
    logger = logging.getLogger('models.planning.Event')

    def __init__(self, name,
            number=0, color=None, chairman="", day=None, start=None, stop=None):
        self.name = name
        self.number = number
        self.color = color or Color('red')
        self.day = day
        self.start = start or datetime.today()
        self.stop = stop or datetime.today()
        self.chairman = chairman

    def __unicode__(self):
        if self.number:
            return unicode("{} {}".format(self.name, self.number))

        return unicode(self.name)
