import datetime
import os
import re
import urlparse
from email.utils import parsedate_tz

import mistune
from flask import Flask, redirect, render_template, request
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from whitenoise import WhiteNoise

import feeds
import mongo
import twitter
import users

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

EMPTY_BLOCK = """<br><br>"""


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRETKEY', '1234567890')

app.wsgi_app = WhiteNoise(app.wsgi_app, root=os.path.join(PROJECT_ROOT, 'static'), prefix='static/')
app.wsgi_app.add_files(os.path.join(PROJECT_ROOT, 'www'))

#
# database
#

db = mongo.connect()


#
# request lifecycle
#

@app.context_processor
def inject_content():
    docs = db.blocks.find({'path': request.path})
    blocks = {d.get('key'): d.get('content') or EMPTY_BLOCK for d in docs}
    return {'content': blocks}


@app.context_processor
def inject_user():
    return {'user': current_user}


#
# login stuff
#


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(username):
    user = users.get_user(username)
    if user:
        user.active = True
        user.authenticated = True
    return user

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = users.get_user(username, password)
        if user and user.is_authenticated():
            login_user(user, remember=True)
            return redirect(request.args.get("next") or '/')
        return redirect('/login')
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


#
# template filters
#

FIGURE_RE = re.compile(r'<figure(.*?)</figure>', re.S)
HN_RE = re.compile(r'<h[1-6](.*?)</h[1-6]>', re.S)
OL_RE = re.compile(r'<ol(.*?)</ol>', re.S)
UL_RE = re.compile(r'<ul(.*?)</ul>', re.S)

@app.template_filter()
def pretreat(value):
    value = FIGURE_RE.sub('', value)
    value = HN_RE.sub('', value)
    value = OL_RE.sub('', value)
    value = UL_RE.sub('', value)
    return value

@app.template_filter()
def pretweet(tweet):
    text = tweet['text']
    urls = tweet.get('entities', {}).get('urls', [])
    for url in urls:
        a = '<a href="%s">%s</a>' % (url['url'], url['display_url'])
        text = text.replace(url['url'], a)
    return text

@app.template_filter()
def created_at(tweet, fmt=None):
    time_tuple = parsedate_tz(tweet['created_at'].strip())
    dt = datetime.datetime(*time_tuple[:6])
    dt = dt - datetime.timedelta(seconds=time_tuple[-1])
    utc_offset = tweet.get('user', {}).get('utc_offset')
    if utc_offset:
        dt = dt + datetime.timedelta(minutes=utc_offset / 60)
    if fmt:
        return dt.strftime(fmt)
    return dt

@app.template_filter()
def markdown(value):
    return mistune.markdown(value)

@app.template_filter()
def slugify(value):
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)

#
# cms methods
#

@app.route('/save', methods=['POST'])
@login_required
def save():

    content = request.form.get('content', '').strip()
    key = request.form.get('key')
    path = request.form.get('path')
    username = request.form.get('user')

    if not path:
        referrer = request.environ.get('HTTP_REFERER')
        path = urlparse.urlparse(referrer).path

    content = mistune.markdown(content)

    doc = {
        'path': path,
        'key': key,
        'content': content,
        'user': username,
    }

    db.blocks.update({'path': path}, {"$set": doc}, upsert=True)

    return content

#
# basic routes
#

@app.route('/')
def index():
    context = {
        'posts': feeds.posts(),
        'mpt_tweets': twitter.mpt_timeline(per_page=1),
        'tag_tweets': twitter.tag_timeline(per_page=2),
    }
    return render_template('index.html', **context)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/casestudies')
def casestudies():
    return render_template('casestudies.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/data')
def data():
    return render_template('data.html')


@app.route('/networking')
def networking():
    return render_template('networking.html')


@app.route('/norms')
def norms():
    return render_template('norms.html')


@app.route('/resources')
def resources():
    return render_template('resources.html')


if __name__ == '__main__':
    app.run(debug=True, port=8000)