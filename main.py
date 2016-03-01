from time import mktime
from datetime import datetime
import logging

from google.appengine.ext import ndb
from webapp2_extras.appengine.auth.models import Unique

from flask import Flask, render_template
import feedparser


app = Flask(__name__)

GOODREADS_RSS_URL = 'https://www.goodreads.com/quotes_of_the_day/rss'


class Quote(ndb.Model):
    text = ndb.StringProperty(required=False)
    author = ndb.StringProperty(required=False)
    # author_link = db.StringProperty(required=False)
    link = ndb.StringProperty(required=False)
    date = ndb.DateTimeProperty(required=False)
    date_modified = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def create_quote(cls, link, date):
        uniques = [
            'Quote.link.%s' % link,
            'Quote.date.%s' % date,
        ]

        # transactionally create the unique quote based on date and link
        # https://webapp-improved.appspot.com/_modules/webapp2_extras/appengine/auth/models.html#Unique
        success, existing = Unique.create_multi(uniques)
        if success:
            # the unique values were created so we can save the quote
            quote = Quote(date=date, link=link)
            quote.put()
            return quote


def read_feed():
    feedparser._HTMLSanitizer.acceptable_elements = []  # cleans up all html tag
    feeds = feedparser.parse(GOODREADS_RSS_URL)

    # q = db.Query('Quote')

    for feed in feeds.entries:

        clearer_date = datetime.fromtimestamp(mktime(feed.published_parsed))

        uniques = ['Quote.link.%s' % feed.link,
                   'Quote.date.%s' % clearer_date, ]
        success, existing = Unique.create_multi(uniques)

        if success:
            quote = Quote()
            quote.date = clearer_date
            parsed_summary = [a for a in feed.summary.splitlines()
                              if a and a != '-']
            quote.text = parsed_summary[0]
            quote.author = parsed_summary[1]
            quote.link = feed.link
            quote.put()
            logging.info(
                'New feed: {}, dated: {} has been inserted into the datastore'
                .format(feed.link, clearer_date)
            )
        else:
            logging.debug('Properties %r are not unique.' % existing)


@app.route('/cron')
def cron():
    read_feed()
    return 'updated quotes'


@app.route('/')
def home():
    quotes = Quote.query().order(-Quote.date).fetch(7)
    return render_template('home.html', quotes=quotes)


if __name__ == '__main__':
    app.run(debug=False)
