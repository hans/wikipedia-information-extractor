import json
import os

from google.appengine.ext import webapp

class BaseHandler(webapp.RequestHandler):
    """ Base RequestHandler to be inherited by all other
        RequestHandlers. """

    JINJA_ENV = None

    def out(self, data):
        """ Write data to client  """
        self.response.write(data)

    def out_json(self, data):
        """ Write json data to client """
        self.response.headers['Content-Type'] = 'application/json'
        self.out(json.dumps(data))

    def out_template(self, filename, data=None):
        """ Render and write a template to client.
            `data` must be a dict if values need to be
            sent to the template """

        self.response.headers['Content-Type'] = 'text/html'
        if data is None:
            data = {}

        # Add other values
        # ---
        data.update({
            'APP_VERSION': os.environ['CURRENT_VERSION_ID'],
            'HOST': self.request.host,
            'PAGE_URL_FULL': self.request.path_url,
            'QUERY_STRING': self.request.query_string,
            'URL': self.request.url,
            'PATH': self.request.path
        })

        template = self.JINJA_ENV.get_template(filename)
        self.out(template.render(data))
