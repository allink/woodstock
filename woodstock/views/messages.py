from django.shortcuts import render_to_response
from django.template import RequestContext

def show_message(request):
    """
    A blank view to show all pending messages.
    """
    return render_to_response('woodstock/messages/view.html', {},
        context_instance = RequestContext(request))