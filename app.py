import sys
import os.path

import json
import logging

from google.appengine.ext import webapp
import jinja2

from handlers import BaseHandler


class MainHandler(BaseHandler):
    def get(self, url):
        template_data = {'param1': 'derp'}

        self.out_template("analyze.html", template_data)

# -------
# WEBAPP
# -------

BaseHandler.JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader('./templates'))

app = webapp.WSGIApplication([
    (r'/analyze/(.+)', MainHandler),
],
debug=False)
