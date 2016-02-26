from django import template
from finance.models import Account


register = template.Library()


@register.filter
def account_type_name(account_type):
    return dict(Account.TYPE)[account_type]
