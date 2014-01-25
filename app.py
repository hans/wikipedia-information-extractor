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
    parser = etree.XMLParser(encoding='utf-8')

    def process(self, url):
        result = urlfetch.fetch(urllib.unquote(url), deadline=20)
        if result.status_code != 200:
            self.error(500)

        document = etree.fromstring(result.content, parser=self.parser)
        # document_content = document.cssselect('#mw-content-text').text()

        # TODO: Extract terms
        # TODO: Extract definitions

        relevant_pages = wikipedia.get_relevant_pages(document)

        data = {
            # TODO
            'terms': [],
            'related': [{'url': wikipedia.page_name_to_link(page),
                         'name': page[1]} for page in relevant_pages]
        }

        return data


class HTMLAnalysisHandler(AnalysisHandler):
    def get(self, url):
        data = self.process(url)
        self.out_template("analyze.html", data)


class JSONAnalysisHandler(AnalysisHandler):
    def get(self, url):
        self.response.headers['Content-Type'] = 'application/json'
        data = self.process(url)
        self.out_json(data)


# -------
# WEBAPP
# -------

BaseHandler.JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader('./templates'))

app = webapp.WSGIApplication([
    (r'/', HomeHandler),
    (r'/analyze/(.+)\.json', JSONAnalysisHandler),
    (r'/analyze/(.+)', HTMLAnalysisHandler),
],
debug=False)
