import os
import urlparse

import pymongo
from flask import Flask, redirect, render_template, request
from flask.ext.login import LoginManager, login_user, logout_user, login_required
from whitenoise import WhiteNoise

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRETKEY', '1234567890')

app.wsgi_app = WhiteNoise(app.wsgi_app, root=os.path.join(PROJECT_ROOT, 'static'))


#
# request lifecycle
#

# @app.before_request
# def before_request():
#     mongo_uri = os.environ.get('MONGOHQ_URL')
#     database = urlparse.urlparse(mongo_uri).path

#     print "!!!!!", database

#     if mongo_uri:
#         conn = pymongo.Connection(mongo_uri)
#         g.db = conn[os.environ.get('MONGOHQ_DB')]
#     else:
#         conn = pymongo.Connection()
#         g.db = conn['openingparliament']


# @app.teardown_request
# def teardown_request(exception):
#     if hasattr(g, 'db'):
#         g.db.connection.disconnect()


# @app.context_processor
# def inject_content():
#     doc = g.db.blocks.find_one({'path': request.path})
#     return {'content': doc.get('content') or EMPTY_BLOCK if doc else EMPTY_BLOCK}


# @app.context_processor
# def inject_admin():
#     return {'admin': True if request.authorization else False}


#
# login stuff
#

class User(object):

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        pass


login_manager = LoginManager()
login_manager.init_app(app)

def login_user(user):
    pass

@login_manager.user_loader
def load_user(userid):
    return User.get(userid)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        # login and validate the user...
        login_user(user, remember=True)
        return redirect(request.args.get("next") or url_for("index"))
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(somewhere)

#
# authentication stuff
#

def check_auth(username, password):
    return username == 'admin' and password == os.environ.get('ADMIN_PASSWORD', '')


def authenticate():
    msg = "This site is not yet available to the public. Please login."
    return Response(msg, 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


#
# template filters
#

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

    if not path:
        referrer = request.environ.get('HTTP_REFERER')
        path = urlparse.urlparse(referrer).path

    doc = {
        'path': path,
        'key': key,
        'content': content,
    }

    g.db.blocks.update({'path': path}, {"$set": doc}, upsert=True)

    return content

#
# basic routes
#

@app.route('/')
def index():
    return render_template('index.html')


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