##############################################################################
##############################################################################
##############################################################################
###
### seriouschange/organise/views.py
###
### Contains the views for site admins to organise things
###
##############################################################################
##############################################################################
##############################################################################

import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.models import User
from django import forms
from django.core.mail import send_mail, send_mass_mail, BadHeaderError

from seriouschange.signup.models import SignupDetails
from seriouschange.organise.models import MailEvent

##############################################################################
#
@login_required
def organise_overview(request):
    """docstring for organise_overview"""
    
    # we want some nice overview stats to make life easier
    people = SignupDetails.objects.all()
    total_count = len(people)
    
    t = datetime.date.today()
    d = datetime.datetime(t.year, t.month, t.day, 0, 0)
    people_today = people.filter(creation_time__gte=d)
    total_today = len(people_today)
    
    people_since_last_login = people.filter(creation_time__gte=request.user.last_login)
    total_since_last_login = len(people_since_last_login)
    
    return render_to_response("overview.html", 
        {'total': {'all': total_count, 'today': total_today, 'recent': total_since_last_login}},
        context_instance=RequestContext(request))
#
##############################################################################


##############################################################################
#
def email_list(request):
    
    campaign_list = MailEvent.objects.all()
    
    return render_to_response("email_list.html",
        {'campaign_list': campaign_list},
        context_instance=RequestContext(request))
#
##############################################################################


##############################################################################
#
class MailEventForm(forms.Form):
    from_address = forms.EmailField(required=True)
    subject = forms.CharField(max_length=255, required=True)
    message = forms.CharField(required=True, widget=forms.Textarea)
    everyone = forms.BooleanField(required=False)
    
    
@login_required
def email_compose(request):
    """docstring for organise_overview"""
    
    print request.POST
    print request.user.email
    message = None
    
    if request.method == "POST":
        form = MailEventForm(request.POST)
        if form.is_valid():
            
            if (not request.POST.has_key('everyone')) or (request.POST['everyone'] != 'on'):
                # test mail
                send_mail(form.cleaned_data['subject'], 
                    form.cleaned_data['message'], 
                    form.cleaned_data['from_address'],
                    [request.user.email,])
                message = "Email has been sent to you - please check it!"
            else:
                # mail everyont
                
                signed_up_people = SignupDetails.objects.all()
                mail_list = [(form.cleaned_data['subject'], form.cleaned_data['message'], 
                    form.cleaned_data['from_address'], [x.email_address,]) for x in signed_up_people]
                
                send_mass_mail(mail_list, fail_silently=True)
                
                message = "This email has been sent to %d people - I hope you meant it :)" % len(mail_list)
        
                mail_event = MailEvent.objects.create(from_address = form.cleaned_data['from_address'],
                    subject = form.cleaned_data['subject'],
                    body = form.cleaned_data['message'],
                    date_sent = datetime.datetime.now(),
                    sender = request.user)
                mail_event.save()
                
                return HttpResponseRedirect("../")
        
    else:
        form = MailEventForm({'from_address': 'hello@seriouschange.org.uk',
            'subject': 'Email subject',
            'message': 'To everyone...'})
        message = None
    
    return render_to_response("email.html", 
        {'form': form, 'message': message},
        context_instance=RequestContext(request))
#
##############################################################################