from dateutil.relativedelta import relativedelta
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import resolve_url
from finance.forms import BudgetForm
from finance.models import Budget
from common.utils import first_day, date_param
from common.views import ListView, CreateView, UpdateView, DeleteView


class BudgetListView(ListView):
  model = Budget
  template_name = 'finance/budgets/list.html'

  def get_date(self):
    return first_day(date_param(self.request, 'date'))

  def get_queryset(self):
    return super().get_queryset()\
      .filter(date=self.get_date())\
      .select_related()\
      .order_by('-type', 'category__name')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    date = self.get_date()
    context['current_month'] = date
    context['previous_month'] = first_day(date - relativedelta(months=1))
    context['next_month'] = first_day(date + relativedelta(months=1))
    return context


class BudgetCreateView(CreateView):
  model = Budget
  template_name = 'finance/budgets/create.html'
  form_class = BudgetForm

  def get_initial(self):
    return {'next': self.request.GET.get('next', resolve_url('budgets-list'))}

  def get_success_url(self):
    return self.request.POST.get('next')

  def get_date(self):
    return first_day(date_param(self.request, 'date'))

  def get_form_kwargs(self):
    kwargs = super().get_form_kwargs()
    kwargs['date'] = self.get_date()
    kwargs['user'] = self.request.user
    return kwargs

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    # define the month range for filter
    date = self.get_date()
    context['current_month'] = date
    context['previous_month'] = first_day(date - relativedelta(months=1))
    context['next_month'] = first_day(date + relativedelta(months=1))
    return context

  def form_valid(self, form):
    form.instance.user = self.request.user
    form.instance.date = form.clean_date()
    form.instance.type = form.cleaned_data['type']
    if form.instance.type == Budget.TYPE_SAVINGS:
      form.instance.category = None
    return super().form_valid(form)


class BudgetUpdateView(UpdateView):
  model = Budget
  form_class = BudgetForm
  template_name = 'finance/budgets/update.html'

  def get_success_url(self):
    return self.request.POST.get('next')

  def get_initial(self):
    return {'next': self.request.GET.get('next', resolve_url('budgets-list')),
            'type': self.object.type,
            'month': self.object.date.month,
            'year': self.object.date.year}

  def get_form_kwargs(self):
    kwargs = super().get_form_kwargs()
    kwargs['date'] = self.object.date
    kwargs['user'] = self.request.user
    return kwargs

  def form_valid(self, form):
    form.instance.type = form.cleaned_data['type']
    return super().form_valid(form)


class BudgetDeleteView(DeleteView):
  model = Budget
  template_name = 'finance/budgets/delete.html'
  success_url = reverse_lazy('budgets-list')
