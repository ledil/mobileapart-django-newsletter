from django.contrib import admin

from mobileapart.django.newsletter.models import Contact
from mobileapart.django.newsletter.models import Newsletter
from mobileapart.django.newsletter.models import MailingList
from mobileapart.django.newsletter.models import MailingStats

from mobileapart.django.newsletter.admin.contact import ContactAdmin
from mobileapart.django.newsletter.admin.newsletter import NewsletterAdmin
from mobileapart.django.newsletter.admin.mailinglist import MailingListAdmin
from mobileapart.django.newsletter.admin.mailingstats import MailingStatsAdmin

admin.site.register(Contact, ContactAdmin)
admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(MailingList, MailingListAdmin)
admin.site.register(MailingStats, MailingStatsAdmin)
