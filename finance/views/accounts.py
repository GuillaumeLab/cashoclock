from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import resolve_url
from finance.forms import AccountCreateForm, AccountUpdateForm
from finance.models import Account
from common.views import CreateView, UpdateView, DeleteView, DetailView
from common.utils import week_range


class AccountDetailView(DetailView):
  model = Account
  template_name = 'finance/accounts/detail.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    end = datetime.now()
    context['debits'] = self.object.get_debit_balance(end=end, payed=True)
    context['credits'] = self.object.get_credit_balance(end=end, payed=True)
    context['total'] = self.object.get_balance(end=end, payed=True)

    # last 60 days balance
    context['history'] = [
      {'date': date,
       'balance': self.object.get_balance(end=date, payed=True)}
      for date in week_range(end - relativedelta(months=4), end)]

    return context


class AccountCreateView(CreateView):
  model = Account
  template_name = 'finance/accounts/create.html'
  form_class = AccountCreateForm

  def get_success_url(self):
    return self.request.POST.get('next')

  def get_initial(self):
    return {'next': self.request.GET.get('next', resolve_url('settings-index'))}

  def form_valid(self, form):
    form.instance.user = self.request.user
    return super().form_valid(form)


class AccountUpdateView(UpdateView):
  model = Account
  template_name = 'finance/accounts/update.html'
  form_class = AccountUpdateForm

  def get_initial(self):
    return {'next': self.request.GET.get('next', resolve_url('settings-index'))}

  def get_success_url(self):
    return self.request.POST.get('next')


class AccountDeleteView(DeleteView):
  model = Account
  template_name = 'finance/accounts/delete.html'
  success_url = reverse_lazy('settings-index')
