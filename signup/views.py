##############################################################################
##############################################################################
##############################################################################
###
### seriouschange/signup/views.py
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
from django.forms import ModelForm, ValidationError, Form
import django.forms as forms

# serious change imports
from seriouschange.signup.models import SignupDetails


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
    postcode = forms.CharField(max_length=9, 
        error_messages = {'required': 'Please enter a valid postcode.'})

    ##########################################################################
    #
    def clean_postcode(self):
        """we use this method to check that the postcode is valid"""
        postcode = self.cleaned_data['postcode']
        
        print "-%s-" % postcode
        
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
    print request.POST
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