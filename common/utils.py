import io
import csv
import calendar
import random
import time
import datetime
from django.conf import settings
from django.http import HttpResponse
from dateutil.rrule import rrule, MONTHLY, DAILY, WEEKLY
from hashids import Hashids
from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit


hashid = Hashids(salt=settings.SECRET_KEY,
                 min_length=6,
                 alphabet='abcdefghijklmnopqrstuvwxyz1234567890')


def random_hashid():
  """ generate a pseudo-random hashid, do NOT use for security """
  random.seed()
  rand = random.randint(1, 999999999) + int(time.time())
  return hashid.encode(rand)


def first_day(date):
  """ first day of the month at midnight """
  return datetime.datetime(date.year, date.month, 1)


def last_day(date):
  """ last day of the month at midnight """
  return datetime.datetime(date.year,
                           date.month,
                           calendar.monthrange(date.year, date.month)[1])


def diff_month(start, end):
  """ difference in months between two dates """
  return (end.year - start.year) * 12 + end.month - start.month


def date_param(request, name, default=datetime.datetime.today()):
  """ get a querystring parameter as date with default """
  value = request.GET.get(name, None)
  if (value is None or value.strip() == '') and default is None:
    return None
  return datetime.datetime.strptime((value or default.strftime('%d/%m/%Y')), '%d/%m/%Y')


def boolean_param(request, name, default=None):
  value = request.GET.get(name, None)
  if value is None:
    return default
  return bool(value) and value.lower() not in ('false', '0')


def day_range(start, end=None, count=None):
  """ generate a range of days between two dates """
  for dt in rrule(DAILY, dtstart=start, until=end, count=count):
    yield dt


def week_range(start, end=None, count=None):
  """ generate a range of weeks between two dates """
  for dt in rrule(WEEKLY, dtstart=start, until=end, count=count):
    yield dt


def biweekly_range(start, end=None, count=None):
  """ generate a range of 2 weeks between two dates """
  for dt in rrule(WEEKLY, dtstart=start, until=end, count=count, interval=2):
    yield dt


def month_range(start, end=None, count=None):
  """ generate a range of months between two dates """

  for dt in rrule(MONTHLY, dtstart=start, until=end, count=count,
                  bymonthday=(start.day, -1), bysetpos=1):
    yield dt


def bimonth_range(start, end=None, count=None):
  """ generate a range of months between two dates """
  for dt in rrule(MONTHLY, dtstart=start, until=end, count=count,
                  interval=2, bymonthday=(start.day, -1), bysetpos=1):
    yield dt


def quaterly_range(start, end=None, count=None):
  """ generate a range of months between two dates """
  for dt in rrule(MONTHLY, dtstart=start, until=end, count=count,
                  interval=4, bymonthday=(start.day, -1), bysetpos=1):
    yield dt


def biannual_range(start, end=None, count=None):
  """ generate a range of months between two dates """
  for dt in rrule(MONTHLY, dtstart=start, until=end, count=count,
                  interval=6, bymonthday=(start.day, -1), bysetpos=1):
    yield dt


def annual_range(start, end=None, count=None):
  """ generate a range of months between two dates """
  for dt in rrule(MONTHLY, dtstart=start, until=end, count=count,
                  interval=12, bymonthday=(start.day, -1), bysetpos=1):
    yield dt


def set_query_parameter(url, param_name, param_value):
  """
  Given a URL, set or replace a query parameter and return the modified URL.
  """
  scheme, netloc, path, query_string, fragment = urlsplit(url)
  query_params = parse_qs(query_string)

  query_params[param_name] = [param_value]
  new_query_string = urlencode(query_params, doseq=True)

  return urlunsplit((scheme, netloc, path, new_query_string, fragment))


def dict_to_csv(data, fieldnames, format_date=True):
  """
  Export dictionary to csv string
  """
  with io.StringIO() as f:
    writer = csv.DictWriter(f, fieldnames)
    writer.writeheader()
    for row in data:
      if not format_date:
        writer.writerow(row)
        continue

      # try to format dates
      formatted_row = {}
      for field in fieldnames:
        if isinstance(row[field], datetime.date):
          formatted_row[field] = row[field].strftime('%Y-%m-%d')
        else:
          formatted_row[field] = row[field]
      writer.writerow(formatted_row)

    return f.getvalue()


def csv_response(data, fieldnames):
  """
  Get a HttpResponse with CSV data
  """
  return HttpResponse(dict_to_csv(data, fieldnames), content_type='text/csv')
