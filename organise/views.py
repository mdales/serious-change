##############################################################################
##############################################################################
##############################################################################
###
### seriouschange/organise/views.py
###
### Copyright Michael Dales (c) 2008. Made available under
### the Affero GNU Public License - see COPYING file for details.
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
from django.core.mail import SMTPConnection, EmailMessage

from seriouschange.signup.models import SignupDetails, GeoData
from seriouschange.organise.models import MailEvent

from seriouschange import settings

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
def _genete_list_of_groups():
    """Given the database of subscribers, work out a list of targetable zones"""

    targets = [('*', 'Everyone'), ('', '')]
    
    geo_list = GeoData.objects.all()
    
    admin_list = set()
    country_list = set()
    
    for g in geo_list:
        if g.admin_area:            
            admin_list.add(g.admin_area)
        if g.country:
            country_list.add(g.country)

    for a in admin_list:
        targets.append(('a:%s' % a, a))
    targets.append(('', ''))
    for c in country_list:
        targets.append(('c:%s' % c, c))
        
    return targets
#
##############################################################################


##############################################################################
#
def _our_send_mass_mail(datatuple, form_address, fail_silently=False, auth_user=None,
                   auth_password=None):
    """Our hacked version of the django send_mass_mail function, which relies
    on django having this patch:
    http://code.djangoproject.com/attachment/ticket/9214/9214-EmailMessage-r9084.diff
    """
    connection = SMTPConnection(username=auth_user, password=auth_password,
                                fail_silently=fail_silently)
    headers = {'From': form_address}
    messages = [EmailMessage(subject, message, sender, recipient, headers=headers)
                for subject, message, sender, recipient in datatuple]
    return connection.send_messages(messages)
#
##############################################################################


##############################################################################
#   
class MailEventForm(forms.Form):
    # we assime always the hello address
    #from_address = forms.EmailField(required=True)
    subject = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'size':'60'}))
    message = forms.CharField(required=True, widget=forms.Textarea)
    target = forms.ChoiceField(required=True)
    preview = forms.BooleanField(required=False, label="Preview only")
    
    
@login_required
def email_compose(request):
    """docstring for organise_overview"""
    
    message = None
    
    if request.method == "POST":
        form = MailEventForm(request.POST)
        form.fields['target'].choices = _genete_list_of_groups()
        if form.is_valid():
            
            if (request.POST.has_key('preview')) and (request.POST['preview'] == 'on'):
                # test mail
                message = "This is a TEST MESSAGE from serious change authored by %s\n\n" % request.user.username +\
                    form.cleaned_data['message'];
                    
                if settings.DEBUG:
                    sender = request.user.email
                else:
                    sender = 'hello@seriouschange.org.uk'
                
                _our_send_mass_mail([(form.cleaned_data['subject'], 
                        message, 'bounce@serioschange.org.uk',
                        [sender,])], 
                    'Serious Change <hello@seriouschange.org.uk>')
                message = "Email has been sent to you - please check it!"
            else:
                # mail everyont
                
                # filter people based on what we asked for
                region = form.cleaned_data['target']
                if region == '*':
                    signed_up_people = SignupDetails.objects.all()
                else:
                    # was it an admin area or country?
                    if region.startswith('a:'):
                        signed_up_people = SignupDetails.objects.filter(location__admin_area=region[2:])
                    elif region.startswith('c:'):
                        signed_up_people = SignupDetails.objects.filter(location__country=region[2:])
                    else:
                        pass #XXX erm
                
                mail_list = [(form.cleaned_data['subject'], form.cleaned_data['message'], 
                    'bounce@seriouschange.org.uk', [x.email_address,]) for x in signed_up_people]
                
                _our_send_mass_mail(mail_list, 
                    'Serious Change <hello@seriouschange.org.uk>', 
                    fail_silently=True)
                
                message = "This email has been sent to %d people - I hope you meant it :)" % len(mail_list)
        
                mail_event = MailEvent.objects.create(from_address = 
                    'Serious Change <hello@seriouschange.org.uk>',
                    subject = form.cleaned_data['subject'],
                    body = form.cleaned_data['message'],
                    date_sent = datetime.datetime.now(),
                    region = region,
                    sender = request.user)

                for person in signed_up_people:
                    mail_event.receivers.add(person)
                mail_event.save()
                
                return HttpResponseRedirect("../")
        
    else:
        form = MailEventForm({'from_address': 'Serious Change <hello@seriouschange.org.uk>',
            'subject': 'Email subject',
            'message': 'To everyone...',
            'preview': True})
        form.fields['target'].choices = _genete_list_of_groups()
        message = None
    
    return render_to_response("email.html", 
        {'form': form, 'message': message},
        context_instance=RequestContext(request))
#
##############################################################################


##############################################################################
#   
@login_required
def email_review(request, email_id):
    
    email = get_object_or_404(MailEvent, pk=email_id)
    message = ''
    receiver_set = email.receivers.get_query_set().all()
    
    # filter based on region
    region = email.region
    if region == '*':
        people_set = SignupDetails.objects.all()
        pretty_print_region = "everyone"
    else:
        # was it an admin area or country?
        if region.startswith('a:'):
            people_set = SignupDetails.objects.filter(location__admin_area=region[2:])
            pretty_print_region = region[2:]
        elif region.startswith('c:'):
            people_set = SignupDetails.objects.filter(location__country=region[2:])
            pretty_print_region = region[2:]
        else:
            raise Http404 #XXX erm
    
    if request.method == "POST":
        # the user wants to send this message to those that haven't had it already
        
        # build our list of new people
        new_people = []
        receiver_list = [x for x in receiver_set]
        for person in people_set:
            try:
                receiver_list.index(person)
            except ValueError:
                new_people.append(person)
        
        # now we have a list of targets, send that email!
        mail_list = [(email.subject, email.body, 
            'bounce@seriouschange.org.uk', [x.email_address,]) for x in new_people]
        
        _our_send_mass_mail(mail_list, 
            'Serious Change <hello@seriouschange.org.uk>', 
            fail_silently=True)
        
        message = "This email has been sent to %d people - I hope you meant it :)" % len(new_people)

        for person in new_people:
            email.receivers.add(person)
        email.save()
        
    count = len(email.receivers.get_query_set().all())
    new_user_count = len(people_set) - count

    return render_to_response("email_review.html", 
        {'email': email, 'message': message, 'count': count,
        'new_user_count': new_user_count,
        'region': pretty_print_region},
        context_instance=RequestContext(request))
#
##############################################################################


##############################################################################
#   
@login_required
def plot_users(request):
    
    point_list = GeoData.objects.exclude(latitude=None, longitude=None)
    
    missing = len(SignupDetails.objects.exclude(location=None).exclude(location__longitude=None))
    
    return render_to_response("mapping.html", {'points': point_list, 
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY},
        context_instance=RequestContext(request))
#
##############################################################################