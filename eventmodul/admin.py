from eventmodul.models import Event, EventAdmin,\
    Participant, ParticipantAdmin, Invitee, InviteeAdmin, Group, GroupAdmin,\
    Salutation, SalutationAdmin

from django.contrib import admin

admin.site.register(Event, EventAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Group,GroupAdmin)
admin.site.register(Invitee, InviteeAdmin)
admin.site.register(Salutation, SalutationAdmin)
