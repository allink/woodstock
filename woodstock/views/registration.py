from woodstock import settings
from woodstock.models import Participant
from woodstock.views import get_redirect_url
from woodstock.views.decorators import registration_required, \
    invitation_required
from woodstock.forms import SetPasswordForm, PasswordChangeForm, \
    ParticipantForm, LostPasswordForm

from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect

def create_participant(request):
    # todo: hier implementieren
    pass

def start(request):
    """
    Start Registration view with login and lost password function
    """
    # todo: hier implementieren
    pass

def lost_password_view(request, template_name='woodstock/registration/lost_password.html'):
    if request.method == 'POST':
        lost_password_form = LostPasswordForm(request.POST)
        if lost_password_form.is_valid():
            lost_password_form.save()
            messages.success(request, settings.MESSAGES_LOST_PASSWORD)
            return HttpResponseRedirect(get_redirect_url(settings.POST_ACTION_REDIRECT_URL))
    if 'lost_password_form' not in locals():
        lost_password_form = LostPasswordForm()
    context = {'lost_password_form':lost_password_form}
    context.update(csrf(request))
    return render_to_response(template_name, context,context_instance = RequestContext(request))

@registration_required
@csrf_protect
def set_new_password(request, set_password_form=SetPasswordForm, template_name='woodstock/registration/set_new_password.html'):
    """
    Displays the set new password form
    """
    user = request.user
    if request.method == 'POST':
        form = set_password_form(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, settings.MESSAGES_PASSWORD_CHANGED)
            return HttpResponseRedirect(get_redirect_url(settings.POST_ACTION_REDIRECT_URL))
    else:
        form = set_password_form(None)
    context = {'form':form}
    context.update(csrf(request))
    return render_to_response(template_name, context,context_instance = RequestContext(request))

@registration_required
@csrf_protect
def change_password(request, password_change_form=PasswordChangeForm, template_name='woodstock/registration/change_password.html'):
    """
    Displays the change password form
    """
    user = request.user
    if request.method == 'POST':
        form = password_change_form(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, settings.MESSAGES_PASSWORD_CHANGED)
            return HttpResponseRedirect(get_redirect_url(settings.POST_ACTION_REDIRECT_URL))
    else:
        form = password_change_form(user)
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

def change_userdata(request, change_userdata_form=ParticipantForm):
    user = request.user
    if request.method == 'POST':
        form = change_userdata_form(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, settings.MESSAGES_USERDATA_CHANGED)
            return HttpResponseRedirect(get_redirect_url(settings.POST_ACTION_REDIRECT_URL))
    else:
        form = change_userdata_form(instance=user)
    context = {'form':form}
    context.update(csrf(request))
    return render_to_response('woodstock/registration/change_userdata.html', context,context_instance = RequestContext(request))

    