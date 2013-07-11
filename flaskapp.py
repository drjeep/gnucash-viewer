import os
from flask import Flask, render_template, request, redirect, url_for, g
from flask_debugtoolbar import DebugToolbarExtension
from gnucash import Session
from utils import get_accounts, get_account_label

# configuration
DEBUG = True
SECRET_KEY = '1234567890'
DEBUG_TB_INTERCEPT_REDIRECTS = False
GNUCASH_SESSION = os.path.join(os.path.dirname(__file__), 'docs/test.gnucash')

app = Flask(__name__)
app.config.from_object(__name__)

toolbar = DebugToolbarExtension(app)


def get_session():
    session = getattr(g, '_session', None)
    if session is None:
        session = g._session = Session(app.config['GNUCASH_SESSION'])
    return session


@app.route('/')
def index(name=None):
    session = get_session()
    root = session.book.get_root_account()
    accounts = []
    for ac in get_accounts(root):
        accounts.append((ac.name, get_account_label(ac)))
    return render_template('index.html', accounts=accounts)


@app.route('/account/')
def account():
    account = request.args.get('account')
    if not account:
        redirect(url_for('index'))
    session = get_session()
    root = session.book.get_root_account()
    ac = root.lookup_by_name(str(account))
    return get_account_label(ac)


@app.teardown_appcontext
def end_session(exception):
    session = getattr(g, '_session', None)
    if session is not None:
        session.end()


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()
