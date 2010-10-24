##################
# Datastore models
##################

from google.appengine.ext import db

class Paste(db.Model):
    # Title, as a string
    title = db.StringProperty(required=True)
    # Content, as HTML
    content = db.TextProperty(required=True)
    # Date created. Set automatically when the model is made.
    created_time = db.DateProperty(auto_now_add=True)
