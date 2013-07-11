from datetime import date
from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import desc
from database import db_session
from models import Account, Transaction, Split
from utils_db import get_accounts, get_account_label

# configuration
DEBUG = True
SECRET_KEY = '1234567890'
DEBUG_TB_INTERCEPT_REDIRECTS = False

app = Flask(__name__)
app.config.from_object(__name__)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def index():
    accounts = []
    for ac in get_accounts():
        accounts.append((ac.name, get_account_label(ac)))
    return render_template('index.html', accounts=accounts)


@app.route('/account/')
def account():
    account = request.args.get('account')
    if not account:
        redirect(url_for('index'))
    ac = Account.query.filter_by(name=account).one()

    data = []
    for split in Split.query.join(Transaction). \
                             filter(Split.account_guid == ac.guid). \
                             filter(Transaction.post_date > date(2012, 02, 29)). \
                             order_by(desc(Transaction.post_date)).all():
        trans = split.transaction
        amount = Decimal(split.value_num / split.value_denom)
        if amount < 0:
            debit, credit = None, amount
        else:
            debit, credit = amount, None
        t_date = trans.post_date
        row = {
            'date': t_date,
            'desc': trans.description,
            'debit': debit,
            'credit': credit,
            'splits': []
        }
        for t_split in Split.query.join(Account).filter(Split.tx_guid == trans.guid).all():
            amount = Decimal(t_split.value_num / t_split.value_denom)
            account = t_split.account
            if amount < 0:
                debit, credit = None, amount
            else:
                debit, credit = amount, None
            row['splits'].append({
                'account': get_account_label(account),
                'debit': debit,
                'credit': credit
            })
        data.append(row)

    return render_template('account.html', account=get_account_label(ac), data=data)


@app.teardown_appcontext
def teardown_appcontext(exception):
    db_session.remove()


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run()
