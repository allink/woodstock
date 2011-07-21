"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.core import exceptions
from django.test import TestCase
from woodstock.models import Event, EventPart, Participant, Salutation
from woodstock import settings

import datetime

class SUBSCRIPTION_ALLOW_MULTIPLE_EVENTS(TestCase):
    fixtures = ('salutation.json',)
    def setUp(self):
        self.events = []
        self.event_parts = []
        date = datetime.datetime.now()
        for i in range(2):
            event = Event.objects.create(slug=str(i), active=True)
            event.translations.create(name='EventName')
            part = EventPart.objects.create(event=event, date_start=date, date_end=date)
            self.events.append(event)
            self.event_parts.append(part)
        self.event_parts.append(EventPart.objects.create(event=self.events[1], date_start=date, date_end=date))
        self.participant = Participant.objects.create(firstname='Marc',surname='Egli', salutation=Salutation.objects.get(pk=1))
        settings.SUBSCRIPTION_ALLOW_MULTIPLE_EVENTS = False
        settings.SUBSCRIPTION_ALLOW_MULTIPLE_EVENTPARTS = True

    def test_multiple_events_in_one_attend_events_call(self):
        self.assertRaises(exceptions.PermissionDenied,self.participant.attend_events,self.event_parts)
        
    def test_multiple_events_in_separate_attend_events_calls(self):
        self.participant.attend_events([self.event_parts[0]])
        self.assertRaises(exceptions.PermissionDenied,self.participant.attend_events,[self.event_parts[1]])
    
    def test_same_event_multiple_parts(self):
        self.assertTrue(self.participant.attend_events(self.event_parts[1:3]))

class SUBSCRIPTION_ALLOW_MULTIPLE_EVENTPARTS(TestCase):
    fixtures = ('salutation.json',)
    def setUp(self):
        self.events = []
        self.event_parts = []
        date = datetime.datetime.now()
        for i in range(2):
            event = Event.objects.create(slug=str(i), active=True)
            event.translations.create(name='EventName')
            self.events.append(event)
            part = EventPart.objects.create(event=event, date_start=date, date_end=date)
            self.event_parts.append(part)
            part = EventPart.objects.create(event=event, date_start=date, date_end=date)
            self.event_parts.append(part)
        self.participant = Participant.objects.create(firstname='Marc',surname='Egli', salutation=Salutation.objects.get(pk=1))
        settings.SUBSCRIPTION_ALLOW_MULTIPLE_EVENTS = True
        settings.SUBSCRIPTION_ALLOW_MULTIPLE_EVENTPARTS = False
    
    def test_multiple_event_parts_of_same_event_in_one_call(self):
        self.assertRaises(exceptions.PermissionDenied,self.participant.attend_events,self.event_parts[0:2])
    
    def test_multiple_event_parts_of_same_event_in_separate_calls(self):
        self.participant.attend_events([self.event_parts[0]])
        self.assertRaises(exceptions.PermissionDenied,self.participant.attend_events,[self.event_parts[1]])
    
    def test_multiple_event_parts_of_multiple_events_in_one_call(self):
        self.assertTrue(self.participant.attend_events(self.event_parts[1:3]))
    