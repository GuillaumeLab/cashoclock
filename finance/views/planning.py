from datetime import datetime
from dateutil.relativedelta import relativedelta

from common.utils import last_day, first_day, month_range
from finance.models import Account, Transaction
from common.views import TemplateView


class PlanningIndexView(TemplateView):
  template_name = 'finance/planning/index.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['start'] = first_day(datetime.today())
    context['end'] = last_day(datetime.today() + relativedelta(months=6))
    context['cash_flow_start'] = first_day(context['start'] - relativedelta(months=2))
    context['cash_flow_end'] = last_day(context['start'] + relativedelta(months=2))

    # incomes vs expenses
    context['incomes_expenses'] = Transaction.objects.cash_flow(
      self.request.user, context['start'], context['end'])

    context['cash_flow'] = Transaction.objects.cash_flow_by_category(
      self.request.user, context['cash_flow_start'], context['cash_flow_end'])

    # assets balance
    assets_range = month_range(context['start'], context['end'])
    context['assets_balance'] = [
      (date, Account.objects.accounts_balance(self.request.user, last_day(date), payed=None))
      for date in assets_range]

    return context
