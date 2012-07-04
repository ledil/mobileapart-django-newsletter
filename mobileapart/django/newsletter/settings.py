from django.conf import settings

DEFAULT_HEADER_SENDER = getattr(settings, 'NEWSLETTER_DEFAULT_HEADER_SENDER', 'Mobileapart Newsletter<noreply@mobileapart.com>')
DEFAULT_HEADER_REPLY = getattr(settings, 'NEWSLETTER_DEFAULT_HEADER_REPLY', DEFAULT_HEADER_SENDER)