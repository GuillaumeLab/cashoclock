from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import password_reset as django_password_reset
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from django.utils.text import ugettext_lazy as _
from django.contrib import messages
from django.db import transaction
from django.views.generic import (
  ListView as DjangoListView,
  TemplateView as DjangoTemplateView,
  CreateView as DjangoCreateView,
  DetailView as DjangoDetailView,
  UpdateView as DjangoUpdateView,
  DeleteView as DjangoDeleteView,
  FormView as DjangoFormView)
from braces.views import LoginRequiredMixin
from common.forms import UserCreationForm, ForgotUsernameForm


class CurrentUserQuerysetMixin(object):
  """
  Filter the queryset for the current user only
  """
  def get_queryset(self):
    if hasattr(self.model, 'user'):
      return self.model.objects.filter(user=self.request.user)
    return super().get_queryset()


class DetailView(LoginRequiredMixin,
                 CurrentUserQuerysetMixin,
                 DjangoDetailView):
  pass


class TemplateView(LoginRequiredMixin,
                   CurrentUserQuerysetMixin,
                   DjangoTemplateView):
  pass


class ListView(LoginRequiredMixin,
               CurrentUserQuerysetMixin,
               DjangoListView):
  pass


class CreateView(LoginRequiredMixin,
                 CurrentUserQuerysetMixin,
                 DjangoCreateView):
  pass


class DeleteView(LoginRequiredMixin,
                 CurrentUserQuerysetMixin,
                 DjangoDeleteView):
  pass


class UpdateView(LoginRequiredMixin,
                 CurrentUserQuerysetMixin,
                 DjangoUpdateView):
  pass


class FormView(LoginRequiredMixin,
               CurrentUserQuerysetMixin,
               DjangoFormView):
  pass


@transaction.atomic
@csrf_protect
def register(request):
  """
  User registration view
  """
  form = UserCreationForm()
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      form.save()
      messages.success(request, _('User created successfully, please login'))
      return redirect('login')
  return render(request, 'common/registration/register.html', {'form': form})


@csrf_protect
def forgot_username(request):
  if request.method == 'POST':
    form = ForgotUsernameForm(request.POST)
    if form.is_valid():
      try:
        form.save(request, from_email='')
        messages.success(request, _('The username was sent to your email address'))
        return redirect('login')
      except OSError:
        messages.error(request, _('Unable to send email, try again later'))
        return redirect('forgot_username')
  else:
    form = ForgotUsernameForm()
  return render(request, 'common/registration/forgot_username.html',
                {'form': form})


@csrf_protect
def password_reset(request, is_admin_site=False,
                   template_name='registration/password_reset_form.html',
                   email_template_name='registration/password_reset_email.html',
                   subject_template_name='registration/password_reset_subject.txt',
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   current_app=None,
                   extra_context=None,
                   html_email_template_name=None):
  """
  wrap the default password_reset view to check for email exceptions
  """
  try:
    return django_password_reset(request, is_admin_site, template_name,
                                 email_template_name, subject_template_name,
                                 password_reset_form, token_generator,
                                 post_reset_redirect, from_email, current_app,
                                 extra_context, html_email_template_name)
  except OSError:
    messages.error(request, _('Unable to send email, try again later'))
    return redirect('password_reset')
