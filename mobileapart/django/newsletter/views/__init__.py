from mobileapart.django.newsletter.models import MailingList, Newsletter, MailingStats
from django.contrib.sites.models import Site
from django.http import Http404
from django.template import RequestContext, Context
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
import traceback
import base64
from datetime import datetime
from django.http import HttpResponse

# unsubscribed
def view_newsletter_unsubscribe(request, nid, cid):
    newsletter = get_object_or_404(Newsletter, uuid=nid)
    already_unsubscribed = False
    try:
        contact = newsletter.mailing_list.subscribers.get(uuid=cid)
        newsletter.mailing_list.subscribers.remove(contact)
        newsletter.mailing_list.unsubscribers.add(contact)
    except:
        already_unsubscribed = True
        contact = newsletter.mailing_list.unsubscribers.get(uuid=cid)
    return render_to_response('newsletter/unsubscribed.html',{
        'newsletter':newsletter,
        'contact':contact,
        'already_unsubscribed':already_unsubscribed,
    },context_instance=RequestContext(request))

# tracking
def view_newsletter_tracking(request, nid, cid):
    newsletter = get_object_or_404(Newsletter, uuid=nid)
    contact = newsletter.mailing_list.subscribers.filter(uuid=cid)
    if (contact.count() == 1):
        m = newsletter.stats.filter(contact__uuid=cid)
        if (m.count() == 0):
            m = MailingStats(contact=contact[0],sent=True, opened=datetime.now(), smtp_error='')
            m.save()
            newsletter.stats.add(m)
        else:
            m = m[0]
            m.opened = datetime.now()
            m.save()
    return HttpResponse(base64.b64decode('R0lGODlhAQABAIAAAAAAAAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='), mimetype='image/gif')

# subscribe
def view_newsletter_subscribe(request, nid, cid):
    newsletter = get_object_or_404(Newsletter, uuid=nid)
    contact = get_object_or_404(newsletter.mailing_list.unsubscribers, uuid=cid)
    newsletter.mailing_list.unsubscribers.remove(contact)
    newsletter.mailing_list.subscribers.add(contact)
    return render_to_response('newsletter/subscribed.html')

# preview
def view_newsletter_preview(request, nid, cid):
    newsletter = get_object_or_404(Newsletter, uuid=nid)

    base_url = "http://"+Site.objects.get_current().domain
    contact = newsletter.mailing_list.subscribers.filter(uuid=cid)
    if (contact.count() == 0):
        contact = newsletter.mailing_list.unsubscribers.filter(uuid=cid)
        if (contact.count() == 0):
            raise Http404()

    unsubscribe = reverse('newsletter_newsletter_unsubscribe',kwargs={'nid':nid,'cid':cid})
    subscribe = reverse('newsletter_newsletter_subscribe',kwargs={'nid':nid,'cid':cid})
    preview = reverse('newsletter_newsletter_preview',kwargs={'nid':nid,'cid':cid})
    tracking = reverse('newsletter_newsletter_tracking',kwargs={'nid':nid,'cid':cid})

    d = {
        'contact':contact,
        'data':newsletter.dictionary,
        'preview_link': base_url+preview,
        'unsubscribe_link': base_url+unsubscribe,
        'subscribe_link': base_url+subscribe,
        'tracking_link': base_url+tracking
    }
    context = Context(d)

    try:
        subject = render_to_string(newsletter.template_subject, context).replace('\n','').replace('\t','').replace('\r','')
    except Exception as es:
        subject = "Missing or broken template %s (%s)" % (newsletter.template_subject, str(traceback.format_exc()))

    d['subject'] = subject
    context = Context(d)

    return render_to_response(newsletter.template_body, context)