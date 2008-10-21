from django.db import models
from django.contrib.auth.models import User


class MailEvent(models.Model):
    sender = models.ForeignKey(User)
    from_address = models.EmailField(default='hello@seriouschange.org.uk')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    date_sent = models.DateTimeField()
    
    def __unicode__(self):
        return self.subject