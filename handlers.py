import json
import logging
from google.appengine.ext import webapp

class BaseHandler(webapp.RequestHandler):
    """ Base RequestHandler to be inherited by all other
        RequestHandlers. """

    def out(self, data):
        """ Write data to client  """
        self.response.write(data)

    def out_json(self, data):
        """ Write json data to client """
        self.response.headers['Content-Type'] = 'application/json'
        self.out(json.dumps, data)
