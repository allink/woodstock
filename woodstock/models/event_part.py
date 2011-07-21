from django.contrib import admin
from django.db import models

#-----------------------------------------------------------------------------
# EventPart
#-----------------------------------------------------------------------------
class EventPartManager(models.Manager):
    use_for_related_fields = True
    def active(self):
        """
        Filters all active Eventparts
        """
        return self.filter(active=True)

event_part_manager = EventPartManager()

class EventPart(models.Model):
    event = models.ForeignKey('woodstock.Event', related_name="parts")
    name = models.CharField(max_length=100)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    signable = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    maximum_participants = models.IntegerField(default=0,
        verbose_name="Maximum Participants",
        help_text="Number of maximum participants or 0 for no limit.")
    
    default_manager = event_part_manager
    objects = event_part_manager
    
    class Meta:
        ordering = ('date_start',)
        verbose_name = "Event Part"
        verbose_name_plural = "Event Parts"
        app_label = 'woodstock'
    
    def __unicode__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        super(EventPart,self).save(*args,**kwargs)
        self.event.update_dates()
    
    def fully_booked(self):
        """Returns true if event is already fully booked"""
        return self.maximum_participants and self.get_participant_count() >= self.maximum_participants
    
    def get_participant_count(self, confirmed_only=True):
        """
        Returns the participant count.
        If confirmed_only is False the overall count is returned.
        """
        if confirmed_only:
            return self.attendances.confirmed().count()
        return self.attendances.all().count()
    get_participant_count.short_description = "Participants"
