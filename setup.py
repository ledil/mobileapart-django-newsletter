import os
from setuptools import setup
from setuptools import find_packages

from mobileapart.django import newsletter


setup(name='mobileapart.django.newsletter',
      version="0.6.2",
      description='A Django app for sending newsletter by email to a contact list.',
      long_description='A Django app for sending newsletter by email to a contact list.',
      keywords='django, newsletter, mailing',
      classifiers=[
          'Framework :: Django',
          'Programming Language :: Python',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: BSD License',
          'Development Status :: 5 - Production/Stable',
          'Topic :: Software Development :: Libraries :: Python Modules',],

      author=newsletter.__author__,
      author_email=newsletter.__email__,
      url='https://github.com/ledil/mobileapart-django-newsletter',

      license=newsletter.__license__,
      packages=find_packages(exclude=['demo']),
      namespace_packages=['mobileapart', 'mobileapart.django'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'html2text',
                        'python-dateutil==1.5',
                        'BeautifulSoup'])
