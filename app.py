import sys
import os.path

import json
import logging

from google.appengine.api import urlfetch
from google.appengine.ext import webapp

import jinja2
from lxml import etree
from lxml.cssselect import CSSSelector

from handlers import BaseHandler
import wikipedia


class HomeHandler(BaseHandler):
    def get(self):
        self.out_template("index.html")


class MainHandler(BaseHandler):
    parser = etree.XMLParser(encoding='utf-8')

    def get(self, url):
        result = urlfetch.fetch(url)
        if result.status_code != 200:
            self.error(500)

        document = etree.fromstring(result.content, parser=self.parser)
        # document_content = document.cssselect('#mw-content-text').text()

        # TODO: Extract terms
        # TODO: Extract definitions

        relevant_pages = wikipedia.get_relevant_pages(document)

        template_data = {
            'relevant_pages': relevant_pages
        }

        self.out_template("analyze.html", template_data)

# -------
# WEBAPP
# -------

BaseHandler.JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader('./templates'))

app = webapp.WSGIApplication([
    (r'/', HomeHandler),
    (r'/analyze/(.+)', MainHandler),
],
debug=False)
