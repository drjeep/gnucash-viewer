import os
from datetime import date
from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for, g
from flask_debugtoolbar import DebugToolbarExtension
from gnucash import Session
from utils import get_accounts, get_account_label

# configuration
DEBUG = True
SECRET_KEY = '1234567890'
DEBUG_TB_INTERCEPT_REDIRECTS = False
GNUCASH_SESSION = os.path.join(os.path.dirname(__file__), 'docs/test.gnucash')

app = Flask(__name__, template_folder='app/templates')
app.config.from_object(__name__)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def index():
    root = g.session.book.get_root_account()
    accounts = []
    for ac in get_accounts(root):
        accounts.append((ac.name, get_account_label(ac)))
    return render_template('index.html', accounts=accounts)


@app.route('/account/')
def account():
    account = request.args.get('account')
    if not account:
        redirect(url_for('index'))
    root = g.session.book.get_root_account()
    ac = root.lookup_by_name(str(account))

    data = []
    for split in ac.GetSplitList():
        trans = split.parent
        amount = Decimal(str(split.GetAmount()))
        if amount < 0:
            debit, credit = None, amount
        else:
            debit, credit = amount, None
        t_date = date.fromtimestamp(trans.GetDate())
        if t_date.year > 2011:
            row = {
                'date': t_date,
                'desc': trans.GetDescription(),
                'debit': debit,
                'credit': credit,
                'splits': []
            }
            for t_split in trans.GetSplitList():
                amount = Decimal(str(t_split.GetAmount()))
                if amount < 0:
                    debit, credit = None, amount
                else:
                    debit, credit = amount, None
                row['splits'].append({
                    'account': get_account_label(t_split.GetAccount()),
                    'debit': debit,
                    'credit': credit
                })
            data.append(row)

    return render_template('account.html', account=get_account_label(ac), data=data)


@app.before_request
def before_request():
    g.session = Session(app.config['GNUCASH_SESSION'])


@app.teardown_request
def teardown_request(exception):
    session = getattr(g, 'session', None)
    if session is not None:
        session.end()


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run()
