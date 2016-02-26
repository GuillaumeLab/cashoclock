from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from common.utils import first_day
from finance.models import Budget

register = template.Library()


@register.simple_tag(takes_context=True)
def get_budget(context, category, month):
  request = context['request']
  date = first_day(month)
  try:
    amount = Budget.objects.get(user=request.user,
                                category__pk=category.pk,
                                date=date).amount
    return intcomma(amount)
  except Budget.DoesNotExist:
    return 0


@register.filter
def budget_type(t):
  return dict(Budget.TYPE)[t]


@register.filter
def is_savings_budget(t):
  return t == Budget.TYPE_SAVINGS


@register.filter
def is_debit_budget(t):
  return t == Budget.TYPE_DEBIT
