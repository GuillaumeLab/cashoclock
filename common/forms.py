from datetime import datetime
from django import forms
from django.shortcuts import resolve_url
from django.template import loader
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.utils.text import ugettext_lazy as _
from finance.models import Category, Account, Transaction


class ForgotUsernameForm(forms.Form):
  """
  Form for forgot username feature
  """
  email = forms.EmailField(label=_('Email'), max_length=255, required=True)

  def clean(self):
    """ check if the email exists """
    cleaned_data = super().clean()
    try:
      User.objects.get(email=cleaned_data['email'])
    except User.DoesNotExist:
      raise forms.ValidationError(_('Email não cadastrado.'))
    return cleaned_data

  def save(self, request,
           email_template_name='common/registration/forgot_username_email.html',
           subject_template_name='common/registration/forgot_username_subject.txt',
           from_email=settings.DEFAULT_FROM_EMAIL):
    """ send the email with username """

    context = {'user': User.objects.get(email=self.cleaned_data['email']),
               'login_url': request.build_absolute_uri(resolve_url('login'))}
    body = loader.render_to_string(email_template_name, context).strip()
    subject = loader.render_to_string(subject_template_name, context).strip()
    send_mail(subject, body, from_email, [context['user'].email])


class UserCreationForm(DjangoUserCreationForm):
  """
  Create a new user and all it's related data
  """
  first_name = forms.CharField(label=_('Nome'), max_length=255, required=True)

  def clean_password1(self):
    password1 = self.cleaned_data.get('password1', '')
    if len(password1) < settings.MIN_PASSWORD_LENGTH:
      raise forms.ValidationError(
        _('Senha deve ter no mínimo 6 caracteres.'))
    return password1

  def save(self, commit=True):
    user = super().save(commit=False)
    user.first_name = self.cleaned_data['first_name']
    user.save()

    # create the categories
    initial_balance_category = Category.objects.create(
      user=user,
      name=_('Saldo Inicial'))

    # create the accounts
    checking_account = Account.objects.create(
      user=user,
      name=_('Conta Corrente'),
      description=_('Conta para os seus gastos diários'),
      is_savings=False)

    savings_account = Account.objects.create(
      user=user,
      name=_('Poupança'),
      description=_('Sua conta poupança, invista seu dinheiro'),
      is_savings=True)

    money_account = Account.objects.create(
      user=user,
      name=_('Dinheiro'),
      description=_('Sua conta para gastos em dinheiro'),
      is_savings=False)

    # initial balance transactions
    Transaction.objects.create(
      user=user,
      account=checking_account,
      category=initial_balance_category,
      date=datetime.today(),
      description=_('Saldo inicial da conta corrente'),
      type=Transaction.TYPE_CREDIT,
      amount=0,
      payed=True)

    Transaction.objects.create(
      user=user,
      account=savings_account,
      category=initial_balance_category,
      date=datetime.today(),
      description=_('Saldo inicial da conta poupança'),
      type=Transaction.TYPE_CREDIT,
      amount=0,
      payed=True)

    Transaction.objects.create(
      user=user,
      account=money_account,
      category=initial_balance_category,
      date=datetime.today(),
      description=_('Saldo inicial da conta dinheiro'),
      type=Transaction.TYPE_CREDIT,
      amount=0,
      payed=True)

    return user
