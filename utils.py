import logging
from decimal import Decimal
from gnucash import Account, GncNumeric, Transaction, Split

log = logging.getLogger(__name__)


def gnc_numeric_from_decimal(decimal_value):
        sign, digits, exponent = decimal_value.as_tuple()

        # convert decimal digits to a fractional numerator
        # equivlent to
        # numerator = int(''.join(digits))
        # but without the wated conversion to string and back,
        # this is probably the same algorithm int() uses
        numerator = 0
        TEN = int(Decimal(0).radix())  # this is always 10
        numerator_place_value = 1
        # add each digit to the final value multiplied by the place value
        # from least significant to most sigificant
        for i in xrange(len(digits) - 1, -1, -1):
            numerator += digits[i] * numerator_place_value
            numerator_place_value *= TEN

        if decimal_value.is_signed():
            numerator = -numerator

        # if the exponent is negative, we use it to set the denominator
        if exponent < 0 :
            denominator = TEN ** (-exponent)
        # if the exponent isn't negative, we bump up the numerator
        # and set the denominator to 1
        else:
            numerator *= TEN ** exponent
            denominator = 1

        return GncNumeric(numerator, denominator)


def get_accounts(root, list=None):
    if list is None:
        list = []
    for child in root.get_children():
        account = Account(instance=child)
        if not account.get_children():
            list.append(account)
        get_accounts(account, list)
    return list


def get_account_ancestors(account, list=None):
    if list is None:
        list = []
    if not account.is_root():
        list.append(account)
        get_account_ancestors(account.get_parent(), list)
    return list


def create_split_transaction(book, bank_acc_name, exp_acc_name, trans_date, description, amount, vat_incl=True):
    """
    @todo: more generic handling of assets/income/expenses/liabilities
    """
    root = book.get_root_account()
    comm_table = book.get_table()
    zar = comm_table.lookup('CURRENCY', 'ZAR')

    bank_acc = root.lookup_by_name(bank_acc_name)
    exp_acc = root.lookup_by_name(exp_acc_name)
    if vat_incl:
        vat_acc = root.lookup_by_name('VAT Claimable')

    trans1 = Transaction(book)
    trans1.BeginEdit()

    num1 = gnc_numeric_from_decimal(amount)  # total
    if vat_incl:
        num2 = gnc_numeric_from_decimal((amount / Decimal('1.14')).quantize(Decimal('0.01')))  # subtotal
        num3 = gnc_numeric_from_decimal(amount - (amount / Decimal('1.14')).quantize(Decimal('0.01')))  # vat
    else:
        num2 = num1  # total

    if bank_acc_name == 'Credit Card':
        num1 = num1.neg()
        num2 = num2.neg()
        try:
            num3 = num3.neg()
        except NameError:
            pass

    split1 = Split(book)
    split1.SetAccount(exp_acc)
    split1.SetParent(trans1)
    split1.SetValue(num2.neg())

    if vat_incl:
        split2 = Split(book)
        split2.SetAccount(vat_acc)
        split2.SetParent(trans1)
        split2.SetValue(num3.neg())

    split3 = Split(book)
    split3.SetAccount(bank_acc)
    split3.SetParent(trans1)
    split3.SetValue(num1)

    trans1.SetCurrency(zar)
    trans1.SetDate(trans_date.day, trans_date.month, trans_date.year)
    trans1.SetDescription(description)

    trans1.CommitEdit()
