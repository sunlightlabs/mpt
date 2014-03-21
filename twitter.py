import os

import requests
import mongo

TAGS = set(('#GlobalMoneyPolitics', '#politicalmoney', '#MoneyPoliticsTransparency'))
SCREEN_NAME = 'mptransparency'

FOAUTH_EMAIL = os.environ.get('FOAUTH_EMAIL')
FOAUTH_PASSWORD = os.environ.get('FOAUTH_PASSWORD')

auth = (FOAUTH_EMAIL, FOAUTH_PASSWORD)


#
# timeline methods
#

def timeline(coll, page=1, per_page=5):
    db = mongo.connect()
    c = db[coll].find({}).sort('id', 1).limit(per_page)

    skip = (page - 1) * per_page
    if skip:
        c = c.skip(skip)

    return list(c)


def mpt_timeline(*args, **kwargs):
    return timeline('mpt_tweets', *args, **kwargs)


def tag_timeline(*args, **kwargs):
    return timeline('tagged_tweets', *args, **kwargs)


#
# import methods
#

def save_tweets(coll, tweets):
    db = mongo.connect()
    for tweet in tweets:
        db[coll].update({'id_str': tweet['id_str']}, {'$set': tweet}, upsert=True)


def tagged_tweets():
    url = 'https://foauth.org/api.twitter.com/1.1/search/tweets.json'
    params = {
        'q': " OR ".join(TAGS),
        'count': 1,
    }
    resp = requests.get(url, params=params, auth=auth)
    if resp.status_code == 200:
        save_tweets('tagged_tweets', resp.json()['statuses'])


def mpt_tweets():
    url = 'https://foauth.org/api.twitter.com/1.1/statuses/user_timeline.json'
    params = {
        'screen_name': SCREEN_NAME,
        'exclude_replies': 'true',
        'include_rts': 'false',
        # 'trim_user': 'true',
        'count': 1,
    }
    resp = requests.get(url, params=params, auth=auth)
    if resp.status_code == 200:
        save_tweets('mpt_tweets', resp.json())


if __name__ == '__main__':
    print "Loading tagged tweets..."
    tagged_tweets()
    print "Loading @MPTransparency tweets..."
    mpt_tweets()
