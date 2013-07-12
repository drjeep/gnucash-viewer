from models import Account


def get_accounts(root=None, list=None):
    if list is None:
        list = []
    if root is None:
        root = Account.query.filter_by(name='Root Account').one()
    for account in Account.query.filter_by(parent_guid=root.guid).all():
        if not Account.query.filter_by(parent_guid=account.guid).count():
            list.append(account)
        get_accounts(account, list)
    return list


def get_account_ancestors(account, list=None):
    if list is None:
        list = []
    if not account.account_type == 'ROOT':
        list.append(account)
        parent = Account.query.filter_by(guid=account.parent_guid).one()
        get_account_ancestors(parent, list)
    return list


def get_account_label(account):
    ancestors = get_account_ancestors(account)
    ancestors.reverse()
    return ':'.join(a.name for a in ancestors)
