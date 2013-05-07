# -*- coding: utf-8 -*-

import os
import setuptools
import setup_util as deps

requires = deps.parse_requirements(['deps.txt'])
depend_links = deps.parse_dependency_links(['deps_txt'])

setuptools.setup(
  name='OWF2013',
  version='0.1dev',
  url='http://www.openworldforum.org/',
  license='LGPL',
  author='Stefane Fermigier',
  author_email='sf@fermigier.com',
  description='We site for the Open World Forum 2013',
  long_description=__doc__,
  packages=['website'],
  zip_safe=False,
  platforms='any',
  setup_requires=['setuptools-git'],
  install_requires=requires,
  dependency_links=depend_links,
  include_package_data=True,
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    ],
)
