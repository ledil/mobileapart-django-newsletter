django-newsletter-ng
====================

django-newsletter-ng


Installation
============

Make sure to install these packages prior to installation :

 * Django >= 1.2
 * html2text
 * BeautifulSoup

how to install with pip:

  $ pip install -e git://github.com/ledil/django-newsletter-ng.git@f99b5a77fbfc916d3dadacbb572f2cd8de1e277c#egg=mobileapart.django.newsletter
  
Configuration
=============

Add following to your settings.py:

  INSTALLED_APPS = (
    '...',
    'mobileapart.django.newsletter',
  )