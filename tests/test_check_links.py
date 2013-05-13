"""
Test the application by clicking on all the links.

Some links are currently blacklisted due to side effects.

TODO: fix this.
"""

import os
from unittest import skipUnless

from flask.ext.linktester import LinkTester

from .base import IntegrationTestCase

RUN_SLOW_TESTS = os.environ.get("RUN_SLOW_TESTS", False)


class BaseTestCase(IntegrationTestCase):
  init_data = True
  no_login = True

  def setUp(self):
    IntegrationTestCase.setUp(self)
    self.crawler = LinkTester(self.client)
    self.crawler.allowed_codes = set([200, 301, 302])


class TestLinks(BaseTestCase):
  init_data = True

  def test_links(self):
    # TODO remove once the english site is ready.
    self.crawler.black_list = set(['/en/'])
    #self.crawler.verbosity = 1
    self.crawler.crawl("/fr/")


@skipUnless(RUN_SLOW_TESTS, "Not running slow tests")
class TestLinksSlow(BaseTestCase):
  init_data = False

  def setUp(self):
    BaseTestCase.setUp(self)

  def test_links(self):
    self.crawler.verbosity = 2
    self.crawler.max_links = 1000
    self.crawler.crawl("/")
