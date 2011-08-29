from woodstock.models.event import Event
from feincms.module.page.extensions.navigation import NavigationExtension, PagePretender
from feincms.content.application.models import reverse

from woodstock import settings
class EventNavigationExtension(NavigationExtension):
    name = 'Event Navigation'
    def children(self, page, **kwargs):
        
        for event in self.get_event_queryset():
            yield PagePretender(
                title=event.translation.name,
                url=self.url_from_event(event),
                tree_id=100
            )
    
    def url_from_event(self, event):
        return reverse(settings.EVENT_DETAIL_URL_NAME, args=(event.slug,))

    def get_event_queryset(self):
        """
        Override this function to use a subset of all events.
        """
        return Event.objects.active()