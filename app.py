import json
import logging
import urllib

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


class AnalysisHandler(BaseHandler):
    def process(self, method, data):
        if method not in ['url', 'term']:
            raise ValueError("method must be one of 'url', 'term'")

        document = None
        if method == 'term':
            page_name = wikipedia.get_page_for_query(data)
            document = wikipedia.fetch_page((None, page_name, None))
        else:
            result = urlfetch.fetch(urllib.unquote(data), deadline=20)
            if result.status_code == 200:
                document = etree.fromstring(result.content, parser=self.parser)

        if document is None:
            self.error(500)

        # document_content = document.cssselect('#mw-content-text').text()

        # TODO: Extract terms
        # TODO: Extract definitions

        relevant_pages = wikipedia.get_relevant_pages(document)

        data = {
            # TODO
            'terms': [],
            'cards': [],
            'shmoop': [],
            'related': [{'url': wikipedia.page_name_to_link(page),
                         'name': page[1]} for page in relevant_pages]
        }

        return data


class HTMLAnalysisHandler(AnalysisHandler):
    def get(self, method, data):
        data = self.process(method, data)
        self.out_template("analyze.html", data)


class JSONAnalysisHandler(AnalysisHandler):
    def get(self, method, data):
        self.response.headers['Content-Type'] = 'application/json'
        data = self.process(method, data)
        self.out_json(data)

# -------
# WEBAPP
# -------

BaseHandler.JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader('./templates'))

app = webapp.WSGIApplication([
    (r'/', HomeHandler),
    (r'/analyze/(url|term)/(.+)\.json$', JSONAnalysisHandler),
    (r'/analyze/(url|term)/(.+)', HTMLAnalysisHandler),
],
debug=False)
