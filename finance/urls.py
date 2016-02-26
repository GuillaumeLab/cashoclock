# flake8: noqa
from django.conf.urls import url
from finance.views import *


urlpatterns = [
  url(r'^$', home.HomeView.as_view(), name='home'),

  # dashboard widgets
  url(r'^w/(?P<name>[\w-]+)/?$', 'finance.views.home.widget', name='widget'),

  # accounts

  url(r'^accounts/create/?$', accounts.AccountCreateView.as_view(), name='accounts-create'),
  url(r'^accounts/(?P<pk>\d+)/?$', accounts.AccountDetailView.as_view(), name='accounts-detail'),
  url(r'^accounts/(?P<pk>\d+)/update/?$', accounts.AccountUpdateView.as_view(), name='accounts-edit'),
  url(r'^accounts/(?P<pk>\d+)/delete/?$', accounts.AccountDeleteView.as_view(), name='accounts-delete'),

  # categories

  url(r'^categories/create/?$', categories.CategoryCreateView.as_view(), name='categories-create'),
  url(r'^categories/(?P<pk>\d+)/update/?$', categories.CategoryUpdateView.as_view(), name='categories-edit'),
  url(r'^categories/(?P<pk>\d+)/delete/?$', categories.CategoryDeleteView.as_view(), name='categories-delete'),
  url(r'^categories/(?P<pk>\d+)/summary/?$', categories.CategorySummaryView.as_view(), name='categories-summary'),

  # transactions

  url(r'^transactions/create/?$', transactions.TransactionCreateView.as_view(), name='transactions-create'),
  url(r'^transactions/(?P<pk>\d+)/edit/?$', transactions.TransactionUpdateView.as_view(), name='transactions-edit'),
  url(r'^transactions/(?P<pk>\d+)/delete/?$', transactions.TransactionDeleteView.as_view(), name='transactions-delete'),
  url(r'^transactions/?$', transactions.TransactionListView.as_view(), name='transactions-list'),

  # budgets

  url(r'^budgets/?$', budgets.BudgetListView.as_view(), name='budgets-list'),
  url(r'^budgets/create/?', budgets.BudgetCreateView.as_view(), name='budgets-create'),
  url(r'^budgets/(?P<pk>\d+)/update/?$', budgets.BudgetUpdateView.as_view(), name='budgets-edit'),
  url(r'^budgets/(?P<pk>\d+)/delete/?$', budgets.BudgetDeleteView.as_view(), name='budgets-delete'),

  # planning

  url(r'^planning/?$', planning.PlanningIndexView.as_view(), name='planning-index'),

  # settings

  url(r'^settings/?$', settings.SettingsView.as_view(), name='settings-index'),

]
