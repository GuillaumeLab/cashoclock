from datetime import datetime

from dateutil.relativedelta import relativedelta
from common.utils import last_day, first_day
from django.shortcuts import resolve_url
from django.http.response import Http404
from finance.models import Transaction
from finance.forms import (
  AccountDetailsFilterForm, TransactionCreateForm, TransactionUpdateForm)
from django.shortcuts import redirect
from common.views import TemplateView, FormView, UpdateView, DeleteView


class TransactionListView(TemplateView):
  template_name = 'finance/transactions/list.html'

  def get_filter_form(self):
    data = self.request.GET.copy()
    if 'start' not in data:
      data['start'] = first_day(datetime.today())
    if 'end' not in data:
      data['end'] = last_day(datetime.today())
    return AccountDetailsFilterForm(self.request.user, data=data)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    form = self.get_filter_form()
    context['filter_form'] = form
    context['accounts'] = self.request.user.account_set.order_by('name')
    context['categories'] = self.request.user.category_set.order_by('name')

    if form.is_valid():
      start = form.cleaned_data['start']
      context['start'] = start
      end = form.cleaned_data['end']
      context['end'] = end

      context['transactions'] = Transaction.objects.get_transactions(
        self.request.user,
        start,
        end,
        form.cleaned_data['account'],
        form.cleaned_data['category'],
        form.cleaned_data['is_payed'],
        form.cleaned_data['type'],
        form.cleaned_data['description'])

      context['credit_balance'] = Transaction.objects.get_credit_balance(
        self.request.user,
        start,
        end,
        form.cleaned_data['account'],
        form.cleaned_data['category'],
        form.cleaned_data['is_payed'],
        form.cleaned_data['type'],
        form.cleaned_data['description'])

      context['debit_balance'] = Transaction.objects.get_debit_balance(
        self.request.user,
        start,
        end,
        form.cleaned_data['account'],
        form.cleaned_data['category'],
        form.cleaned_data['is_payed'],
        form.cleaned_data['type'],
        form.cleaned_data['description'])

      context['total_balance'] = Transaction.objects.get_balance(
        self.request.user,
        end=end,
        accounts=form.cleaned_data['account'],
        categories=form.cleaned_data['category'],
        payed=form.cleaned_data['is_payed'],
        type=form.cleaned_data['type'],
        description=form.cleaned_data['description'])

      # next and previous months links
      context['current_month'] = start

      previous_month = first_day(start - relativedelta(months=1))
      context['previous_month'] = previous_month, last_day(previous_month)

      next_month = first_day(start + relativedelta(months=1))
      context['next_month'] = next_month, last_day(next_month)

    return context


class TransactionCreateView(FormView):
  model = Transaction
  template_name = 'finance/transactions/create.html'
  form_class = TransactionCreateForm

  def get_form_kwargs(self):
    kwargs = super().get_form_kwargs()
    kwargs['user'] = self.request.user
    return kwargs

  def get_initial(self):
    return {'next': self.request.GET.get('next', resolve_url('transactions-list'))}

  def get_success_url(self):
    return self.request.POST.get('next')

  def form_valid(self, form):
    form.instance.user = self.request.user
    if int(form.cleaned_data['type']) == Transaction.TYPE_TRANSFER:
      form.instance.transfer(form.cleaned_data['transfer'])
    else:
      form.instance.type = form.cleaned_data['type']
      installments = form.cleaned_data.get('installments')
      period = form.cleaned_data.get('period')
      form.instance.create_transaction(installments, period)
    return redirect(self.get_success_url())


class TransactionUpdateView(UpdateView):
  model = Transaction
  template_name = 'finance/transactions/update.html'
  form_class = TransactionUpdateForm

  def get_form_kwargs(self):
    kwargs = super().get_form_kwargs()
    kwargs['user'] = self.request.user
    return kwargs

  def get_initial(self):
    return {'next': self.request.GET.get('next', resolve_url('transactions-list'))}

  def get_success_url(self):
    return self.request.POST.get('next')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['recurrence'] = self.object.recurrence_related
    return context

  def form_valid(self, form):
    form.instance.type = form.cleaned_data['type']
    return super().form_valid(form)


class TransactionDeleteView(DeleteView):
  model = Transaction
  template_name = 'finance/transactions/delete.html'

  def get_success_url(self):
    return resolve_url('transactions-list')

  def get_context_data(self, *args, **kwargs):
    context = super().get_context_data(*args, **kwargs)
    context['recurrence'] = self.object.recurrence_related
    return context

  def delete(self, *args, **kwargs):
    if 'not-payed' in self.request.POST:
      self.get_object().recurrence_related.filter(payed=False).delete()
      return redirect(self.get_success_url())
    if 'one' in self.request.POST:
      t = self.get_object().transfer_related
      if t:
        t.delete()
      return super().delete(*args, **kwargs)
    if 'all' in self.request.POST:
      self.get_object().recurrence_related.delete()
      return redirect(self.get_success_url())
    raise Http404()
