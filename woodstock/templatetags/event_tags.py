from django import template
from woodstock.models import EventPart

register = template.Library()

class GetEventPartsNode(template.Node):
    def __init__(self, variable_name=None):
        self.variable_name = variable_name
    def render(self, context):
        if self.variable_name is None:
            return u''
        if 'person' not in context:
            return u''
        if 'group_object' not in context:
            return u''
        person = context['person']
        event = context['group_object']
        event_parts = EventPart.objects.filter(event=event).filter(attendances__participant=person)
        context[self.variable_name] = event_parts
        return u''

def get_subscribed_event_parts(parser, token):
    args = token.split_contents()
    if len(args) != 3 or args[1] != 'as':
        raise template.TemplateSyntaxError("'get_subscribed_event_parts' tag requires an as argument")
    return GetEventPartsNode(variable_name=args[2])
get_subscribed_event_parts = register.tag('get_subscribed_event_parts', get_subscribed_event_parts)
