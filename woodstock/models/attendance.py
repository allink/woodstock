from django.contrib import admin
from django.db import models

import datetime

#-----------------------------------------------------------------------------
# Attendance
#-----------------------------------------------------------------------------
class AttendanceManager(models.Manager):
    use_for_related_fields = True
        
    def confirmed(self):
        return self.filter(confirmed=True)
    
    def unconfirmed(self):
        return self.filter(confirmed=False)

    def attended(self):
        return self.filter(attended=True)
    
    def pending(self):
        """
        All attendances in the future
        """
        return self.filter(event_part__date_start__gt=datetime.datetime.now())

attendance_manager = AttendanceManager()

class Attendance(models.Model):
    participant = models.ForeignKey('woodstock.Participant', related_name='attendances')
    event_part = models.ForeignKey('woodstock.EventPart', related_name='attendances')
    confirmed = models.BooleanField(default=False)
    attended = models.BooleanField(default=True)
    date_registred = models.DateTimeField(default=datetime.datetime.now(), verbose_name="Signup Date")
    
    default_manager = attendance_manager
    objects = attendance_manager
    
    class Meta:
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
        app_label = 'woodstock'
    
    def __unicode__(self):
        return u'%s is attending %s' % (self.participant, self.event_part)
