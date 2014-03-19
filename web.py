import os
import urlparse

import mistune
import pymongo
from flask import Flask, redirect, render_template, request
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from whitenoise import WhiteNoise

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRETKEY', '1234567890')

app.wsgi_app = WhiteNoise(app.wsgi_app, root=os.path.join(PROJECT_ROOT, 'static'), prefix='static/')
app.wsgi_app.add_files(os.path.join(PROJECT_ROOT, 'www'))


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


@app.context_processor
def inject_user():
    return {'user': current_user}


#
# login stuff
#

class User(object):

    def __init__(self, user_id):
        self.id = user_id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @property
    def is_admin(self):
        return self.is_authenticated() and self.is_active() and not self.is_anonymous()


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        user = load_user(request.form.get('username'))
        login_user(user, remember=True)
        return redirect(request.args.get("next") or '/')
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


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
    # key = request.form.get('key')
    # path = request.form.get('path')

    # if not path:
    #     referrer = request.environ.get('HTTP_REFERER')
    #     path = urlparse.urlparse(referrer).path

    content = mistune.markdown(content)

    # doc = {
    #     'path': path,
    #     'key': key,
    #     'content': content,
    # }

    # g.db.blocks.update({'path': path}, {"$set": doc}, upsert=True)

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