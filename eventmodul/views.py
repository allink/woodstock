from eventmodul.models import Event, Customer, Participant, NewsletterMail, Group, Feedback
from eventmodul.forms import ParticipantForm, FeedbackForm

from feincms.content.application.models import reverse

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import translation
from django.conf import settings

import os

def index(request):
    return render_to_response(
        'index.html',
        {
            'events': Event.objects.order_by('date'),
        },
        context_instance = RequestContext(request),
    )
    

def detail(request, object_id):
    return render_to_response(
        'detail.html',
        {
            'event': Event.objects.filter(id=object_id).all()[0]
        },
        context_instance = RequestContext(request),
    )

def signup(request, object_id):
    event = Event.objects.filter(id=object_id).all()[0]
    success = False
    fully_booked = False
    if request.method == 'POST':
        p = Participant(language=translation.get_language())
        form = ParticipantForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            success = form.instance.attend_event(event)
            fully_booked = not success
    else:
        if request.session.get('customer_id', False):
            customer=Customer.objects.filter(id=request.session.get('customer_id'))[0]
            form = ParticipantForm(instance=customer)
        else:
            form = ParticipantForm()
    return render_to_response(
        'signup.html',
        {
            'form': form,
            'event': event,
            'success': success,
            'fully_booked': fully_booked
        },
        context_instance = RequestContext(request),
    )

def feedback(request, object_id):
    event = Event.objects.filter(id=object_id).all()[0]
    if request.method == 'POST':
        feedback = Feedback(event=event)
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            form.save()
            return render_to_response('feedback_thanks.html',{}, context_instance=RequestContext(request))
    else:
        form = FeedbackForm()
    return render_to_response('feedback.html',
        {
            'event':event,
            'form':form,
        },
        context_instance = RequestContext(request),
    )
    
def feedback_success(request):
    return render_to_response('feedback_thanks.html', context_instance=RequestContext(request))
    
def feedback_landing(request, event_id, language):
    if language == 'de':
        url = '/anmeldung/%s/feedback/' % event_id
    elif language == 'fr':
        url = '/inscription/%s/feedback/' % event_id
    else:
        url = '/registration/%s/feedback/' % event_id
    # url = reverse('eventmodul.urls/event_feedback', kwargs={'object_id':event_id})
    if not 'HTTP_USER_AGENT' in request.META.keys() or 'msie 6.' in request.META['HTTP_USER_AGENT'].lower():
        return HttpResponseRedirect(url)
    url = '/#!/%s/' % (url[1:-1].replace('/','_'),)
    return HttpResponseRedirect(url)

def newsletter_signup(request, email_hash):
    participant = Participant.objects.filter(email_hash=email_hash)
    if participant.count() == 0:
        return HttpResponseRedirect('/')
    participant = participant[0]
    if participant.events.count() == 0:
        return HttpResponseRedirect('/')
    event = participant.events.all()[0]
    return render_to_response(
        'newsletter/signup.html',
        {
            'NEWSLETTER_URL': settings.NEWSLETTER_URL,
            'participant':participant,
            'event': event,
            'weblink': '',
            'confirm': participant.confirmed,
        },
        context_instance = RequestContext(request),
    )

def newsletter_ping(request, mail_hash, path):
    mail = NewsletterMail.objects.filter(mail_hash=mail_hash)
    if mail.count()>0:
        mail = mail[0]
        mail.viewed=True
        mail.save()
    return HttpResponseRedirect(settings.NEWSLETTER_URL + path)


def newsletter_view(request, mail_hash):
    mail = NewsletterMail.objects.filter(mail_hash=mail_hash)
    if mail.count() != 1:
        return HttpResponseRedirect('/')
    mail=mail[0]
    mail.viewed=True
    mail.save()
    return HttpResponse(mail.get_content())


def newsletter_landing(request, mail_hash):
    mail = NewsletterMail.objects.filter(mail_hash=mail_hash)
    if mail.count() != 1:
        return HttpResponseRedirect('/')
    mail = mail[0]
    if type(mail.person) == type(Customer()):
        mail.person.done=True
        mail.person.save()
        request.session['customer_id'] = mail.person.id
        link = '/#!/' + settings.EVENTS_PAGE_URL[translation.get_language()] + '/' + str(mail.job.group.event.id) + '/'
        return HttpResponseRedirect(link)        
    return HttpResponseRedirect('/')
