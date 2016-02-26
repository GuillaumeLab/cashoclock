import re
from django import template
from common import utils
from django.template.base import VariableDoesNotExist

register = template.Library()


@register.filter
def month_range(start, end):
  return utils.month_range(start, end)


@register.filter
def first_day(date):
  return utils.first_day(date)


@register.filter
def last_day(date):
  return utils.last_day(date)


@register.simple_tag(takes_context=True)
def active(context, pattern, klass='active'):
  path = context['request'].path
  if re.search(pattern, path):
    return klass
  return ''


@register.simple_tag(takes_context=True)
def active_account(context, account, klass='active'):
  return active(context, '^/accounts/%s/?' % account.hashid, klass)


@register.filter
def sub(value, arg):
  return value - arg


class UpdateQuerystringNode(template.Node):
  def __init__(self, **kwargs):
    self.kwargs = kwargs

  def render(self, context):
    request = context['request']
    query_dict = request.GET.copy()
    for k, v in self.kwargs.items():
      if v == '-1':
        if k in query_dict:
          del query_dict[k]
      else:
        try:
          query_dict[k] = template.Variable(v).resolve(context)
        except VariableDoesNotExist:
          query_dict[k] = v
    return '%s?%s' % (request.path, query_dict.urlencode())


@register.tag
def update_querystring(parser, token):
  """
  From /?foo=bar, {% update_querystring foo=baz %}
  will output foo=baz.
  """
  bits = token.split_contents()
  return UpdateQuerystringNode(**dict([bit.split('=') for bit in bits[1:]]))


@register.simple_tag(takes_context=True)
def absolute_uri(context, url):
  return context['request'].build_absolute_uri(url)
