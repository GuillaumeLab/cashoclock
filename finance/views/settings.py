from datetime import datetime
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import resolve_url
from common.views import TemplateView, FormView
from finance.views.home import _accounts_with_balance


class SettingsView(TemplateView):
  template_name = 'finance/settings/index.html'

  def get_categories(self):
    return self.request.user.category_set.order_by('name')

  def get_accounts(self):
    return _accounts_with_balance(self.request, end=datetime.now())

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['accounts'] = self.get_accounts()
    context['categories'] = self.get_categories()
    context['change_password_form'] = PasswordChangeForm(self.request.user)
    return context


class PasswordChangeView(FormView):
  template_name = 'finance/settings/change_password.html'

  def get_form(self, form_class=None):
    if self.request.method == 'POST':
      return PasswordChangeForm(self.request.user, data=self.request.POST)
    return PasswordChangeForm(self.request.user)

  def get_success_url(self):
    return resolve_url('settings-index')
