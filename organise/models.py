from django.db import models
from django.contrib.auth.models import User

from seriouschange.signup.models import SignupDetails

class MailEvent(models.Model):
    sender = models.ForeignKey(User)
    from_address = models.EmailField(default='hello@seriouschange.org.uk')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    date_sent = models.DateTimeField()
    
    # we want to track who has received this so we can send it out to
    # people who haev signed up since
    receivers = models.ManyToManyField(SignupDetails, related_name="receivers_set")
    
    def __unicode__(self):
        return self.subject