from datetime import datetime, timedelta
from django import forms
from django.utils.text import ugettext_lazy as _
from finance.models import Account, Transaction, Budget, Category, WishListItem
from common.utils import first_day, last_day


class CategoryForm(forms.ModelForm):
  next = forms.CharField(required=False)

  class Meta:
    model = Category
    exclude = ('hashid', 'user')


class AccountUpdateForm(forms.ModelForm):
  next = forms.CharField(required=False)

  class Meta:
    model = Account
    localized_fields = '__all__'
    exclude = ('hashid', 'user',)


class AccountCreateForm(AccountUpdateForm):
  initial_balance = forms.DecimalField(label=_('Saldo Inicial'),
                                       max_digits=15,
                                       decimal_places=2,
                                       localize=True,
                                       required=False)


class AccountDetailsFilterForm(forms.Form):
  description = forms.CharField(label=_('Description'), required=False)
  start = forms.DateField(label=_('Start'), required=False)
  end = forms.DateField(label=_('End'), required=False)
  type = forms.IntegerField(
    required=False,
    label=_('Tipo'),
    widget=forms.Select(choices=[(None, _('')),
                                 (Transaction.TYPE_DEBIT, 'Debit'),
                                 (Transaction.TYPE_CREDIT, 'Credit')]))
  account = forms.ModelMultipleChoiceField(
    queryset=Account.objects,
    required=False,
    label=_('Conta'))
  category = forms.ModelMultipleChoiceField(
    queryset=Category.objects,
    required=False,
    label=_('Categoria'))
  is_payed = forms.NullBooleanField(
    required=False,
    label=_('Pago?'),
    widget=forms.Select(choices=[(None, _('')),
                                 (True, _('Yes')),
                                 (False, _('No'))]))

  def __init__(self, user, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['category'].queryset = user.category_set.order_by('name')
    self.fields['account'].queryset = user.account_set.order_by('name')

  def clean_start(self):
    return self.cleaned_data['start'] or first_day(datetime.today())

  def clean_end(self):
    return self.cleaned_data['end'] or last_day(datetime.today())


class TransactionForm(forms.ModelForm):
  next = forms.CharField(required=False)
  type = forms.ChoiceField(label=_('Type'),
                           choices=Transaction.TYPE,
                           initial=Transaction.TYPE_DEBIT)
  transfer = forms.ModelChoiceField(label=_('Transfer To'),
                                    queryset=Account.objects,
                                    required=False)

  class Meta:
    model = Transaction
    localized_fields = '__all__'
    exclude = ('hashid', 'recurrence_key', 'transfer_key', 'user',
               'installment_number', 'installment_total', 'type',)

  def __init__(self, user, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.user = user
    self.fields['description'].widget = forms.TextInput()
    self.fields['category'].required = False
    if self.instance.pk and self.instance.is_transfer:
      self.fields['category'].queryset = user.category_set \
        .filter(name='Transferência')
    else:
      self.fields['category'].queryset = user.category_set.exclude(
        name='Transferência').order_by('name')
    self.fields["transfer"].queryset = user.account_set.order_by("name")

  def clean(self):
    cleaned_data = super().clean()

    # for transfers, check the transfer_account field
    if (int(cleaned_data.get('type', -1)) == Transaction.TYPE_TRANSFER and
       not cleaned_data.get('transfer', None)):
      raise forms.ValidationError({'transfer': _('This field is required.')})

    # can't select Transferência category when not creating a transfer
    if int(self.cleaned_data['type']) == Transaction.TYPE_TRANSFER:
      transfer_category = Category.transfer_category(self.user)
      if self.cleaned_data['category'] == transfer_category:
        raise forms.ValidationError({'category': _('This field is required.')})

    # for debit and credit, check the category field
    if (int(cleaned_data.get('type', -1)) != Transaction.TYPE_TRANSFER and
       not cleaned_data.get('category', None)):
      raise forms.ValidationError({'category': _('This field is required.')})

    # for transfers, accounts must be different
    if int(cleaned_data.get('type', -1)) == Transaction.TYPE_TRANSFER:
      if cleaned_data.get('transfer') == cleaned_data.get('account'):
        acc = cleaned_data.get('account')
        raise forms.ValidationError(
          {'transfer': _('Account must not be %s' % acc.name)})

    return cleaned_data


class TransactionCreateForm(TransactionForm):
  is_recurrent = forms.BooleanField(label=_('Recurring Transaction'),
                                    required=False)
  installments = forms.IntegerField(min_value=1, label=_('Installments'),
                                    required=False, initial='1')
  period = forms.ChoiceField(label=_('Period'),
                             required=False,
                             choices=Transaction.PERIOD,
                             initial=Transaction.MONTHLY)


class TransactionUpdateForm(TransactionForm):
  def clean_type(self):
    """
    Transfers can't edit the transaction type
    """
    instance = getattr(self, 'instance', None)
    ttype = self.cleaned_data['type']
    if instance and instance.pk:
      if instance.is_transfer:
        return instance.type
      else:
        # can't select transfer
        if int(ttype) in (Transaction.TYPE_CREDIT, Transaction.TYPE_DEBIT):
          return ttype
        else:
          return instance.type
    return ttype

  def clean_category(self):
    """
    Non editable category for transfer
    """
    instance = getattr(self, 'instance', None)
    if instance and instance.pk and instance.is_transfer:
      return instance.category
    else:
      return self.cleaned_data['category']


class BudgetForm(forms.ModelForm):
  MONTHS = [
    (1, _('January')),
    (2, _('February')),
    (3, _('March')),
    (4, _('April')),
    (5, _('May')),
    (6, _('June')),
    (7, _('July')),
    (8, _('August')),
    (9, _('September')),
    (10, _('October')),
    (11, _('November')),
    (12, _('December'))]
  YEARS = [(y, str(y)) for y in range(datetime.today().year - 5,
                                      datetime.today().year + 5)]

  next = forms.CharField(required=False)
  type = forms.ChoiceField(label=_('Type'),
                           choices=[(None, '---------'),
                                    (Budget.TYPE_DEBIT, _('Debit')),
                                    (Budget.TYPE_CREDIT, _('Credit')),
                                    (Budget.TYPE_SAVINGS, _('Investment'))])
  month = forms.ChoiceField(label=_('Month'),
                            choices=MONTHS,
                            initial=datetime.today().month)
  year = forms.ChoiceField(label=_('Year'),
                           choices=YEARS,
                           initial=datetime.today().year)

  class Meta:
    model = Budget
    localized_fields = '__all__'
    exclude = ('hashid', 'user', 'type', 'date',)

  def __init__(self, date, user, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.date = date
    self.fields['month'].initial = self.date.month
    self.fields['year'].initial = self.date.year
    self.user = user
    self.fields['category'].queryset = (user.category_set
                                        .exclude(name=_('Transfer'))
                                        .order_by('name'))

  def clean_date(self):
    return datetime(int(self.cleaned_data['year']),
                    int(self.cleaned_data['month']),
                    1)

  def clean(self):
    cleaned_data = super().clean()
    btype = cleaned_data.get('type', -1)
    category = cleaned_data.get('category')
    date = self.clean_date()

    # category is required when type=debit or credit
    if int(btype) in (Budget.TYPE_CREDIT, Budget.TYPE_DEBIT) and not category:
      raise forms.ValidationError({'category': _('This field is required.')})

    # check if budget already exists
    if not self.instance or not self.instance.pk:
      budget_count = self.user.budget_set \
        .filter(category=category, date=date, type=btype) \
        .count()
      if budget_count > 0:
        raise forms.ValidationError(
          _('A budget for this month and category already exists.'))

    # can't select Transferência category
    transfer_category = Category.transfer_category(self.user)
    if cleaned_data.get('category', None) == transfer_category:
      raise forms.ValidationError({'category': _('This field is required.')})

    return cleaned_data


class ReportIncomesExpensesFilterForm(forms.Form):
  date_from = forms.DateField(label=_('Data Inicial'), required=False)
  date_to = forms.DateField(label=_('Data Final'), required=False)
  only_payed = forms.BooleanField(label=_('Somente Pagos'), required=False)

  def clean(self):
    cleaned_data = super().clean()

    cleaned_data['only_payed'] = cleaned_data['only_payed'] or False
    cleaned_data['date_from'] = (
      cleaned_data['date_from'] or
      first_day(datetime.today() - timedelta(days=30 * 6)))
    cleaned_data['date_to'] = (
      cleaned_data['date_to'] or
      first_day(datetime.today() + timedelta(days=30 * 5)))

    return cleaned_data


class WishListItemForm(forms.ModelForm):
  next = forms.CharField(required=False)

  class Meta:
    model = WishListItem
    localized_fields = '__all__'
    exclude = ('user',)
