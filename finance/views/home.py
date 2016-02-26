from dateutil.relativedelta import relativedelta
from datetime import datetime
from calendar import monthrange
from common.utils import last_day, first_day, date_param, month_range, boolean_param
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.db.models import Sum
from django.shortcuts import render
from finance.models import Transaction
from finance.models import Budget, Account
from common.views import TemplateView

WIDGET_WHITELIST = [
  'accounts_panel',
  'incomes_expenses_per_day',
  'incomes_expenses_per_month',
  'top_expenses_per_category',
  'assets_balance',
  'cashflow_panel',
  'budgets_panel'
]


def _accounts_with_balance(request, start=None, end=None, payed=True):
  """ Get a list of accounts and their balance and the total balance sum """
  accounts = [
    (acc, acc.get_balance(start=start, end=end, payed=payed))
    for acc in Account.objects.get_queryset(request.user).order_by('name')]
  return accounts, sum(acc[1] for acc in accounts)


@login_required
def widget(request, name):
  if name not in WIDGET_WHITELIST:
    raise Http404()
  return globals()[name](request)


def accounts_panel(request):
  start = date_param(request, 'start', default=None)
  end = date_param(request, 'end', default=last_day(datetime.today()))
  payed = boolean_param(request, 'payed', None)
  data = _accounts_with_balance(request, start, end, payed=payed)
  return render(request, 'finance/home/_accounts_panel.html',
                {'start': start, 'end': end, 'payed': payed, 'data': data})


def incomes_expenses_per_day(request):
  start = date_param(request, 'start', default=first_day(datetime.today()))
  end = date_param(request, 'end', default=last_day(datetime.today()))
  cash_flow = Transaction.objects.cash_flow_by_day(request.user, start, end)
  return render(request, 'finance/home/_incomes_expenses_per_day.html',
                {'start': start, 'end': end, 'data': cash_flow})


def incomes_expenses_per_month(request):
  start = date_param(request, 'start', first_day(datetime.today() - relativedelta(months=12)))
  end = date_param(request, 'end', last_day(datetime.today()))
  cash_flow = Transaction.objects.cash_flow(request.user, start, end)
  return render(request, 'finance/home/_incomes_expenses_per_month.html',
                {'start': start, 'end': end, 'data': cash_flow})


def top_expenses_per_category(request):
  start = date_param(request, 'start', default=first_day(datetime.today()))
  end = date_param(request, 'end', default=last_day(datetime.today()))
  expenses = request.user.transaction_set.exclude(
      category__name='Transferência'
    ).filter(
      type=Transaction.TYPE_DEBIT,
      date__gte=start,
      date__lte=end
    ).values(
      'category__name'
    ).annotate(
      Sum('amount')
    )
  return render(request, 'finance/home/_top_expenses_per_category.html',
                {'start': start,
                 'end': end,
                 'data': sorted(expenses,
                                key=lambda x: x['amount__sum'],
                                reverse=True)[:10]})


def cashflow_panel(request):
  start = date_param(request, 'start', first_day(datetime.today()))
  end = date_param(request, 'end', last_day(datetime.today()))

  incomes = Transaction.objects.get_credit_balance(request.user, start, end, payed=True)
  expenses = Transaction.objects.get_debit_balance(request.user, start, end, payed=True)

  # calculate percentage of incomes vs expenses
  percent = 0
  if incomes > 0 or expenses > 0:
    bigger = max(incomes, expenses)
    smaller = min(incomes, expenses)
    percent = smaller / bigger * 100
  if incomes == 0 and expenses == 0:
    incomes_percent = 0
    expenses_percent = 0
  elif incomes >= expenses:
    incomes_percent = 100
    expenses_percent = percent
  else:
    incomes_percent = percent
    expenses_percent = 100

  return render(request, 'finance/home/_cashflow_panel.html',
                {'start': start,
                 'end': end,
                 'incomes': incomes,
                 'incomes_percent': incomes_percent,
                 'expenses': expenses,
                 'expenses_percent': expenses_percent})


def assets_balance(request):
  start = first_day(date_param(request, 'start', datetime.today() - relativedelta(months=12)))
  end = last_day(date_param(request, 'end', datetime.today()))
  data = [
    (d, Account.objects.accounts_balance(request.user, last_day(d)))
    for d in month_range(start, end)]
  return render(request, 'finance/home/_assets_balance.html',
                {'start': start, 'end': end, 'data': data})


def budgets_panel(request):
  context = {'start': first_day(date_param(request, 'start', datetime.today()))}
  context['budgets'] = Budget.objects.get_queryset(request.user).filter(date=context['start'])

  # average budgets completion
  if context['budgets']:
    percent_complete_sum = sum(budget.percent_complete for budget in context['budgets'])
    percent_complete_avg = percent_complete_sum / len(context['budgets'])
    context['budget_complete_avg'] = percent_complete_avg

    if first_day(datetime.today()) > context['start']:
      # past month, use the last day
      expected_day = last_day(context['start']).timetuple().tm_mday
    elif first_day(datetime.today()) < context['start']:
      # future month, use first day
      expected_day = 1
    else:
      # current month, use current day
      expected_day = datetime.today().timetuple().tm_mday

    num_days_in_month = monthrange(context['start'].timetuple().tm_year,
                                   context['start'].timetuple().tm_mon)[1]
    context['budget_complete_avg_expected'] = (100 / num_days_in_month) * expected_day

  return render(request, 'finance/home/_budgets_panel.html', context)


class HomeView(TemplateView):
  template_name = 'finance/home/index.html'
