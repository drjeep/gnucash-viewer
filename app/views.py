from datetime import date
from decimal import Decimal
from flask import render_template
from app import app, db
from models import Account, Transaction, Split
from utils import get_accounts, get_account_label


@app.route('/')
def index():
    accounts = []
    for ac in get_accounts():
        accounts.append((ac.guid, get_account_label(ac)))
    return render_template('index.html', accounts=accounts)


@app.route('/account/<guid>/')
def account(guid):
    ac = Account.query.filter_by(guid=guid).one()

    data = []
    for split in Split.query.join(Transaction). \
                             filter(Split.account_guid == ac.guid). \
                             filter(Transaction.post_date > date(2012, 02, 29)). \
                             order_by(db.desc(Transaction.post_date)).all():
        trans = split.transaction
        amount = Decimal(split.value_num) / Decimal(split.value_denom)
        if amount < 0:
            debit, credit = None, amount
        else:
            debit, credit = amount, None
        t_date = trans.post_date
        row = {
            'date': t_date.strftime('%Y-%m-%d'),
            'desc': trans.description,
            'debit': debit,
            'credit': credit,
            'splits': []
        }
#        for t_split in Split.query.join(Account).filter(Split.tx_guid == trans.guid).all():
#            amount = Decimal(t_split.value_num / t_split.value_denom)
#            account = t_split.account
#            if amount < 0:
#                debit, credit = None, amount
#            else:
#                debit, credit = amount, None
#            row['splits'].append({
#                'account': get_account_label(account),
#                'debit': debit,
#                'credit': credit
#            })
        data.append(row)

    return render_template('account.html', account=get_account_label(ac), data=data)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500
