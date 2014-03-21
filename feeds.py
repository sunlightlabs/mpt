import datetime
from time import mktime

import feedparser
import mongo

FEEDS = (
    ('Sunlight Foundation', 'http://sunlightfoundation.com/blog/rss/'),
    # ('Global Integrity', 'http://www.globalintegrity.org/blog/feed/'),
)

TAGS = set((
    'globalmoneypolitics',
    'moneypoliticstransparency',
    'mpt',
    'politicalmoney',
))


def posts(page=1, per_page=10):
    skip = (page - 1) * per_page
    db = mongo.connect()
    c = db.posts.find({}).sort('published', 1).limit(per_page)
    if skip:
        c = c.skip(skip)
    return list(c)


def save_post(post):
    db = mongo.connect()
    db.posts.update({'id': post['id']}, {'$set': post}, upsert=True)


def refresh():
    for feed_title, feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for post in feed['entries']:
            tags = set(t['term'].lower() for t in post.get('tags', []))
            if tags & TAGS:
                post['feed'] = feed_title
                post['published_parsed'] = datetime.datetime.fromtimestamp(mktime(post['published_parsed']))
                save_post(post)


if __name__ == '__main__':
    print "Refreshing feeds..."
    refresh()
