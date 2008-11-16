##############################################################################
##############################################################################
##############################################################################
###
### seriouschange/signup/views.py
###
### Copyright Michael Dales (c) 2008. Made available under
### the Affero GNU Public License - see COPYING file for details.
###
### Contains the views for the initial basic sign up web site
###
##############################################################################
##############################################################################
##############################################################################

# standard python imports
import datetime
import re

# standard django imports
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.forms import ModelForm, ValidationError, Form
import django.forms as forms

# serious change imports
from seriouschange.signup.models import SignupDetails
from seriouschange.signup.country import non_uk_countries

#from facebook import Facebook

##############################################################################
#
def _validate_postcode(postcode):
    """Function to validate postcodes by francis"""
    
    # Our test postcode
    if re.match("^zz9\s*9z[zy]$", postcode, re.I):
        return True

    # See http://www.govtalk.gov.uk/gdsc/html/noframes/PostCode-2-1-Release.htm
    _in  = 'ABDEFGHJLNPQRSTUWXYZ';
    fst = 'ABCDEFGHIJKLMNOPRSTUWYZ';
    sec = 'ABCDEFGHJKLMNOPQRSTUVWXY';
    thd = 'ABCDEFGHJKSTUW';
    fth = 'ABEHMNPRVWXY';
    num0 = '123456789'; # Technically allowed in spec, but none exist
    num = '0123456789';
    nom = '0123456789';

    match1 = '^[%s][%s]\s*[%s][%s][%s]$' % \
        (fst, num0, nom, _in, _in)
    match2 = '^[%s][%s][%s]\s*[%s][%s][%s]$' % \
        (fst, num0, num, nom, _in, _in)
    match3 = '^[%s][%s][%s]\s*[%s][%s][%s]$' % \
        (fst, sec, num, nom, _in, _in)
    match4 = '^[%s][%s][%s][%s]\s*[%s][%s][%s]$' % \
        (fst, sec, num0, num, nom, _in, _in)
    match5 = '^[%s][%s][%s]\s*[%s][%s][%s]$' % \
        (fst, num0, thd, nom, _in, _in)
    match6 = '^[%s][%s][%s][%s]\s*[%s][%s][%s]$' % \
        (fst, sec, num0, fth, nom, _in, _in)
        
    match_list = [match1, match2, match3, match4, match5, match6]
    
    pass_val = False
    for match_pattern in match_list:
        if re.match(match_pattern, postcode, re.I):
            pass_val = True
            break
        
    return pass_val
#
##############################################################################



##############################################################################
#
class SignupDetailsForm(Form):
    email_address = forms.EmailField(error_messages = 
        {'required': 'Please enter a valid email address.',
        'invalid': 'Please enter a valid email address.'})
    postcode = forms.CharField(max_length=9, label="Postcode", required=False,
        error_messages = {'required': 'Please enter a valid postcode.'})
    country = forms.ChoiceField(choices=non_uk_countries)
    non_resident = forms.BooleanField(label="Non UK resident", required=False)

    ##########################################################################
    #
    def clean_postcode(self):
        
        if self.is_valid():        
            """we use this method to check that the postcode is valid"""
            postcode = self.cleaned_data['postcode']
               
            try:
                if self.data['non_resident']:
                    return postcode
            except:
                pass
                                
            if len(postcode) == 0:
                raise ValidationError('Please enter a valid postcode.')
            
            if not _validate_postcode(postcode):
                raise ValidationError('Please enter a valid postcode.')
        
            return postcode
    #
    ##########################################################################
    
#
##############################################################################

EMAIL_SUBJECT = "Save iPods and fun fairs from Climate Change"
EMAIL_BODY = """Hi - 

Just found these people, who are stopping Climate Change in
a new way, without the hippies or the denialists.

I think you'll like it.

http://www.seriouschange.org.uk/

<your name>"""



##############################################################################
#
def signup_page(request):
    """This is the basic signup view - asks users for details and then
    forwards them to a 'well done' page."""
    
    if request.method == 'POST':
        signup_form = SignupDetailsForm(request.POST)
        if signup_form.is_valid():
            #new_signup = signup_form.save(commit=False)
            new_signup = SignupDetails()
            new_signup.email_address = signup_form.cleaned_data['email_address']
            new_signup.postcode = signup_form.cleaned_data['postcode']
            new_signup.creation_time = datetime.datetime.now()
            new_signup.creation_ipaddr = request.META['REMOTE_ADDR']
            new_signup.version_string = request.POST['version']
            if signup_form.cleaned_data['non_resident']:
                new_signup.country = signup_form.data['country']
            else:
                new_signup.country = "GB"
            new_signup.save()
            
            # return to the main org view after creation
            return render_to_response('welldone.html', 
                {'email_subject': EMAIL_SUBJECT, 
                'email_body': EMAIL_BODY})
        else:
            # any errors is used to invoke a little bit of javascript 
            # that moves the focus of the page to the form
            any_errors = True
                    
    else:
        signup_form = SignupDetailsForm()
        any_errors = False
        
    return render_to_response('signup.html', {'form': signup_form, 'error': any_errors})
#
##############################################################################


##############################################################################
#
def signup_facebook(request):
    
    # old keys no longer valid, need to get from settings
    #fb = Facebook(settings.FACEBOOK1, settings.FACEBOOK2)
    
    if 'session_key' in request.session and 'uid' in request.session:
        fb.session_key = request.session['session_key']
        fb.uid = request.session['uid']
    else:
        
        try:
            fb.auth_token = request.GET['auth_token']
        except KeyError:
            # Send user to the Facebook to login
            return HttpResponseRedirect(fb.get_login_url())

        # getSession sets the session_key and uid
        # Store these in the cookie so we don't have to get them again
        fb.auth.getSession()
        request.session['session_key'] = fb.session_key
        request.session['uid'] = fb.uid

    
        
    info = fb.users.getInfo([fb.uid], ['name', 'current_location', 'email_hashes'])[0]
    
    return render_to_response('facebook.html', {'info': info, 'fb': fb})
#
##############################################################################
