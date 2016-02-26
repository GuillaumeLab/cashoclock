from django import template
from finance.models import WishListItem

register = template.Library()


@register.filter
def priority_str(priority):
  return dict(WishListItem.PRIORITIES)[priority]
