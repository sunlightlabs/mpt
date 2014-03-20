import os

import requests
import mongo

TAGS = set(('#MoneyPolitics',))

FOAUTH_EMAIL = os.environ.get('FOAUTH_EMAIL')
FOAUTH_PASSWORD = os.environ.get('FOAUTH_PASSWORD')

auth = (FOAUTH_EMAIL, FOAUTH_PASSWORD)

def tagged_tweets():
    url = 'https://foauth.org/api.twitter.com/1.1/search/tweets.json'
    params = {
        'q': " OR ".join(TAGS),
        'count': 1,
    }
    resp = requests.get(url, params=params, auth=auth)
    print resp.json()

def mpt_tweets():
    url = 'https://foauth.org/api.twitter.com/1.1/statuses/user_timeline.json'
    params = {
        'screen_name': 'jcarbaugh',
        'exclude_replies': 'true',
        'include_rts': 'false',
        # 'trim_user': 'true',
        'count': 1,
    }
    resp = requests.get(url, params=params, auth=auth)
    print resp.json()

if __name__ == '__main__':
    # tagged_tweets()
    mpt_tweets()
