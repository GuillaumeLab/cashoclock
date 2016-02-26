from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import resolve_url, get_object_or_404
from finance.forms import CategoryForm
from finance.models import Category
from common.views import CreateView, UpdateView, DeleteView, TemplateView
from common.utils import first_day, last_day


class CategorySummaryView(TemplateView):
  template_name = 'finance/categories/summary.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    category = get_object_or_404(self.request.user.category_set, pk=self.kwargs['pk'])
    one_month_ago = first_day(datetime.today()) - relativedelta(months=1)
    two_months_ago = first_day(datetime.today() - relativedelta(months=2))

    context.update({
      'category': category,
      'one_month_ago': one_month_ago,
      'two_months_ago': two_months_ago,
      'one_month_ago_credit': category.get_credit_balance(
        start=one_month_ago,
        end=last_day(one_month_ago)),
      'one_month_ago_debit': category.get_debit_balance(
        start=one_month_ago,
        end=last_day(one_month_ago)),
      'two_months_ago_credit': category.get_credit_balance(
        start=two_months_ago,
        end=last_day(two_months_ago)),
      'two_months_ago_debit': category.get_debit_balance(
        start=two_months_ago,
        end=last_day(two_months_ago))})

    return context


class CategoryCreateView(CreateView):
  model = Category
  template_name = 'finance/categories/create.html'
  form_class = CategoryForm

  def get_initial(self):
    return {'next': self.request.GET.get('next', resolve_url('settings-index'))}

  def get_success_url(self):
    return self.request.POST.get('next')

  def form_valid(self, form):
    form.instance.user = self.request.user
    return super().form_valid(form)


class CategoryUpdateView(UpdateView):
  model = Category
  template_name = 'finance/categories/update.html'
  form_class = CategoryForm

  def get_initial(self):
    return {'next': self.request.GET.get('next', resolve_url('settings-index'))}

  def get_success_url(self):
    return self.request.POST.get('next')


class CategoryDeleteView(DeleteView):
  model = Category
  template_name = 'finance/categories/delete.html'
  success_url = reverse_lazy('settings-index')
