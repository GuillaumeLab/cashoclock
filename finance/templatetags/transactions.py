from django import template
from finance.models import Transaction

register = template.Library()


@register.filter
def type_str(trans_type):
    return dict(Transaction.TYPE)[trans_type]


@register.filter
def transaction_color(transaction):
    if transaction.amount == 0 or transaction.type == Transaction.TYPE_CREDIT:
        return 'success'
    else:
        return 'danger'


@register.filter
def amount_color(amount):
    if amount == 0:
        return ''
    elif amount < 0:
        return 'danger'
    else:
        return 'success'
