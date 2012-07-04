from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
from django.contrib.sites.models import Site
from mobileapart.django.newsletter.settings import DEFAULT_HEADER_REPLY
from mobileapart.django.newsletter.settings import DEFAULT_HEADER_SENDER
from mobileapart.django.newsletter.utils import html2text
from django.template import Context, Template
from django.template.loader import render_to_string
import traceback
from django.utils.encoding import force_unicode
from django.conf.global_settings import LANGUAGES
from django.db import IntegrityError
from django.core.urlresolvers import reverse
import time
import hashlib
from django.db.models.signals import post_save
import uuid
from django.utils.simplejson import simplejson
from django.core.mail import EmailMultiAlternatives

class Contact(models.Model):
    """Contact for emailing"""
    uuid = models.CharField(max_length=41, unique=True, db_index=True)
    email = models.EmailField(_('email'), unique=True)
    first_name = models.CharField(_('first name'), max_length=50, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=True)
    language = models.CharField(_('Language'), max_length=5, choices=LANGUAGES, default='en')

    subscriber = models.BooleanField(_('subscriber'), default=True)
    valid = models.BooleanField(_('valid email'), default=True)

    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    modification_date = models.DateTimeField(_('modification date'), auto_now=True)

    def __unicode__(self):
        if self.first_name and self.last_name:
            contact_name = '%s %s (%s) - %s' % (self.last_name, self.first_name, self.email, self.uuid)
        else:
            contact_name = self.email + ' - ' +self.uuid
        return contact_name

class MailingList(models.Model):
    """Mailing list"""
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    subscribers = models.ManyToManyField(Contact, verbose_name=_('subscribers'),
                                         related_name='mailinglist_subscriber')
    unsubscribers = models.ManyToManyField(Contact, verbose_name=_('unsubscribers'),
                                           related_name='mailinglist_unsubscriber',
                                           null=True, blank=True)

    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    modification_date = models.DateTimeField(_('modification date'), auto_now=True)

    def subscribers_count(self):
        return self.subscribers.all().count()
    subscribers_count.short_description = _('subscribers')

    def unsubscribers_count(self):
        return self.unsubscribers.all().count()
    unsubscribers_count.short_description = _('unsubscribers')

    def __unicode__(self):
        return self.name

class MailingStats(models.Model):
    contact = models.ForeignKey(Contact, related_name='mailingstats_contact')
    sent = models.BooleanField(default=False)
    opened = models.DateTimeField(blank=True,null=True)
    smtp_error = models.TextField(default='',blank=True,null=True)

class Newsletter(models.Model):
    """Newsletter to be sended to contacts"""
    DRAFT = 0
    WAITING = 1
    SENDING = 2
    SENT = 4
    CANCELED = 5

    STATUS_CHOICES = ((DRAFT, _('draft')),
                      (WAITING, _('waiting sending')),
                      (SENDING, _('sending')),
                      (SENT, _('sent')),
                      (CANCELED, _('canceled')),
                      )

    template_base_body = models.CharField(_('Template Filename Base Body'), max_length=255, help_text=_('relative to TEMPLATE_DIR'), default=_('newsletter/example.html'))
    template_body = models.CharField(_('Template Filename Body'), max_length=255, help_text=_('relative to TEMPLATE_DIR'), default=_('newsletter/example.html'))
    template_subject = models.CharField(_('Template Filename Subject'), max_length=255, help_text=_('relative to TEMPLATE_DIR'), default=_('newsletter/example.html'))

    uuid = models.CharField(max_length=41, unique=True, db_index=True)

    dictionary = models.TextField(_('Dictionary'), help_text=_('JSON dictionary used for template parsing'), default='{}')

    mailing_list = models.ForeignKey(MailingList, verbose_name=_('mailing list'))
    stats = models.ManyToManyField(MailingStats, verbose_name=_('Stats'), blank=True, null=True)

    test_contacts = models.ManyToManyField(Contact, verbose_name=_('test contacts'),
                                           blank=True, null=True)

    header_sender = models.CharField(_('sender'), max_length=255,
                                     default=DEFAULT_HEADER_SENDER)
    header_reply = models.CharField(_('reply to'), max_length=255,
                                    default=DEFAULT_HEADER_REPLY)

    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=DRAFT)
    sending_date = models.DateTimeField(_('sending date'), default=datetime.now)

    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    modification_date = models.DateTimeField(_('modification date'), auto_now=True)

    def _send_contact(self, base_url, contact):
        unsubscribe = reverse('newsletter_newsletter_unsubscribe',kwargs={'nid':self.uuid,'cid':contact.uuid})
        preview = reverse('newsletter_newsletter_preview',kwargs={'nid':self.uuid,'cid':contact.uuid})
        tracking = reverse('newsletter_newsletter_tracking',kwargs={'nid':self.uuid,'cid':contact.uuid})
        subscribe = reverse('newsletter_newsletter_subscribe',kwargs={'nid':self.uuid,'cid':contact.uuid})

        d = {
            'contact':contact,
            'data':simplejson.loads(self.dictionary),
            'preview_link': base_url+preview,
            'unsubscribe_link': base_url+unsubscribe,
            'tracking_link': base_url+tracking,
            'subscribe_link': base_url+subscribe
        }
        context = Context(d)

        try:
            subject = render_to_string(self.template_subject, context).replace('\n','').replace('\t','').replace('\r','')
        except Exception as es:
            subject = "Missing or broken template %s (%s)" % (self.template_subject, str(traceback.format_exc()))

        d['subject'] = subject
        context = Context(d)

        try:
            html_content = render_to_string(self.template_body, context)
        except Exception as es:
            html_content = "<h1>Missing or broken template %s</h1><br/>%s" % (self.template_body, str(traceback.format_exc()))
        text_content = html2text(html_content)

        text_content = force_unicode(text_content)
        subject = force_unicode(subject)

        msg = EmailMultiAlternatives(subject, text_content, self.header_sender, [contact.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def send_test(self):
        all_contacts = self.test_contacts.all()
        base_url = "http://"+Site.objects.get_current().domain

        for contact in all_contacts:
            self._send_contact(base_url, contact)

    def save(self, force_insert=False, force_update=False):
        try:
            simplejson.loads(self.dictionary)
        except:
            raise IntegrityError(_('Invalid json'))
        models.Model.save(self, force_insert, force_update)

### SIGNALS
def create_contact(sender, instance, created, **kwargs):
    if created:
        data = uuid.uuid4().hex+' '+str(time.time())
        instance.uuid = hashlib.sha1(data+str(instance.id)).hexdigest()
        instance.save()

def create_newsletter(sender, instance, created, **kwargs):
    if created:
        data = uuid.uuid4().hex+' '+str(time.time())
        instance.uuid = hashlib.sha1(data+str(instance.id)).hexdigest()
        instance.save()

post_save.connect(create_contact, sender=Contact)
post_save.connect(create_newsletter, sender=Newsletter)
