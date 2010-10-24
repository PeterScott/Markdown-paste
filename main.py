from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app, login_required
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
import logging, os
import models
from markdown2 import markdown
import datetime

class SavePaste(webapp.RequestHandler):
    def post(self):
        text = self.request.get('text')
        if text is None or text == '':
            self.error(400)
            self.response.out.write('<h1>Error 400: Paste must not be empty.</h1>\n')
            return

        title = self.request.get('title') or datetime.date.today().strftime('%B %d, %Y')
        
        # Save the data
        paste = models.Paste(content=markdown(text), title=title)
        paste.put()
        self.redirect('/p/' + str(paste.key()))

class ViewPaste(webapp.RequestHandler):
    def get(self):
        # URLs are of the form "/p/[key]", and if the key is not given
        # then they see the front page.
        key_str = self.request.path[3:]

        # Check in memcache for cached page
        content = memcache.get('paste:' + key_str)
        if content is None:
            try:
                paste = db.get(db.Key(key_str))
            except db.BadKeyError:
                logging.info("Bad key: %s" % key_str)
                paste = None
            if paste is None:
                self.error(404)
                self.response.out.write('<h1>No such paste exists.</h1>')
                return
            template_values = {"content": paste.content, 
                               "created_time": paste.created_time.strftime('%B %d, %Y'),
                               "title": paste.title}
            path = os.path.join(os.path.dirname(__file__), 'templates', 'view.html')
            content = template.render(path, template_values)
            memcache.add('paste:' + key_str, content)

        # Send cache-control headers and the content
        del self.response.headers['Expires']
        self.response.headers['Cache-Control'] = 'public, max-age=600000' # about 1 week
        self.response.out.write(content)


##################
# App setup code
##################

application = webapp.WSGIApplication([('/save', SavePaste), ('/p/.*', ViewPaste)])

def main():
    logging.getLogger().setLevel(logging.INFO)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
