from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from finance import urls as app_urls
from django.views.i18n import javascript_catalog

js_info_dict = {
    'packages': ('finance', 'common'),
}

urlpatterns = [
  url(r'^', include(app_urls)),
  url(r'^admin/', include(admin.site.urls)),

  # i18n

  url(r'^jsi18n/$', javascript_catalog, js_info_dict),

  # auth views

  url(r'^accounts/register/?$', 'common.views.register', name='register'),
  url(r'^accounts/forgot_username/?$', 'common.views.forgot_username', name='forgot_username'),

  url(r'^accounts/login/$', auth_views.login,
      {'template_name': 'common/registration/login.html'},
      name='login'),

  url(r'^accounts/logout/$', auth_views.logout,
      {'next_page': '/accounts/login'}, name='logout'),

  url(r'^accounts/password_change/$', auth_views.password_change,
      {'post_change_redirect': 'settings-index',
       'template_name': 'common/registration/password_change_form.html'},
      name='password_change'),

  url(r'^accounts/password_reset/$', 'common.views.password_reset',
      {'post_reset_redirect': 'login',
       'template_name': 'common/registration/password_reset_form.html'},
      name='password_reset'),

  url(
    r'^accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    auth_views.password_reset_confirm,
    {'post_reset_redirect': 'login',
     'template_name': 'common/registration/password_reset_confirm.html'},
    name='password_reset_confirm'),
]
