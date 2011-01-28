from woodstock.models import Participant
from woodstock.views.decorators import registration_required, \
    invitation_required

from feincms.content.application.models import reverse

from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import translation
from django.views.decorators.csrf import csrf_protect

def create_participant(request):
    pass

def start(request):
    """
    Start Registration view with login and lost password function
    """
    #todo: hier implementieren
    pass

@registration_required
@csrf_protect
def set_new_password(request, set_password_form=SetPasswordForm):
    """
    Presents the set new password form
    """
    if request.method == 'POST':
        form = set_password_form(user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = set_password_form(None)
    context = {'form':form}
    context.update(csrf(request))
    return render_to_response(template_name, context,context_instance = RequestContext(request))

def activate(request):
    """
    Activates a participant
    """
    if not isinstance(request.user, Participant):
        return HttpResponseRedirect('/')
    request.user.activate()
    return render_to_response('woodstock/registration/activation_completed.html',
        {'user':request.user},context_instance = RequestContext(request))
    