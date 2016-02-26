import time
import random
from decimal import Decimal
from hashids import Hashids
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.http.response import Http404
from django.core.validators import MinValueValidator
from django.db import models, transaction, connection
from django.db.models import Sum
from django.db.models.signals import post_save
from django.utils.text import ugettext_lazy as _
from django.conf import settings
from django.dispatch import receiver
from common.utils import (
  first_day, last_day, week_range, biweekly_range, month_range, day_range,
  bimonth_range, quaterly_range, biannual_range, annual_range)

hashid = Hashids(salt=settings.SECRET_KEY,
                 min_length=6,
                 alphabet='abcdefghijklmnopqrstuvwxyz1234567890')


def random_hashid():
  """ generate a pseudo-random hashid, do NOT use for security """
  random.seed()
  rand = random.randint(1, 999999999) + int(time.time())
  return hashid.encode(rand)


@receiver(post_save)
def save_hashid(sender, **kwargs):
  instance = kwargs['instance']
  if 'hashid' in sender._meta.get_all_field_names() and not instance.hashid:
    instance.hashid = hashid.encode(instance.pk)
    instance.save()


class BaseManager(models.Manager):
  def get_queryset(self, user=None):
    qs = super().get_queryset()
    if user:
      return qs.filter(user__pk=user.pk)
    return qs

  def by_id(self, pk, user):
    return self.get_queryset(user).filter(pk=pk)

  def by_hashid_or_404(self, hashid, user):
    try:
      return self.get_queryset(user).filter(hashid=hashid).get()
    except self.model.DoesNotExist:
      raise Http404()

  def by_id_or_404(self, pk, user):
    try:
      return self.by_id(pk, user).get()
    except self.model.DoesNotExist:
      raise Http404()


class AccountManager(BaseManager):
  def accounts_balance(self, user, date, payed=True):
    accounts = self.get_queryset(user)
    return sum(acc.get_balance(end=date, payed=payed) for acc in accounts)


class Account(models.Model):
  hashid = models.CharField(_('Hash'), max_length=255, null=True, blank=True, db_index=True)
  user = models.ForeignKey(User, verbose_name=_('User'))
  name = models.CharField(_('Name'), max_length=255)
  description = models.TextField(_('Description'), null=True, blank=True)
  is_savings = models.BooleanField(_('Investment Account?'), default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  objects = AccountManager()

  def __str__(self):
    return self.name

  def get_absolute_url(self):
    return reverse('accounts-detail', kwargs={'slug': self.hashid})

  def get_credit_balance(self, start=None, end=None, payed=True):
    return Transaction.objects.get_credit_balance(
      self.user,
      accounts=[self],
      start=start,
      end=end,
      payed=payed)

  def get_debit_balance(self, start=None, end=None, payed=True):
    return Transaction.objects.get_debit_balance(
      self.user,
      accounts=[self],
      start=start,
      end=end,
      payed=payed)

  def get_balance(self, start=None, end=None, payed=True):
    return Transaction.objects.get_balance(
      self.user,
      accounts=[self],
      start=start,
      end=end,
      payed=payed)


class CategoryManager(BaseManager):
  pass


class Category(models.Model):
  hashid = models.CharField(_('Hash'), max_length=255, null=True, blank=True, db_index=True)
  user = models.ForeignKey(User, verbose_name=_('User'))
  name = models.CharField(_('Name'), max_length=255)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  objects = CategoryManager()

  def __str__(self):
    return self.name

  @staticmethod
  def transfer_category(user):
    return user.category_set.filter(name='Transferência').get()

  def get_credit_balance(self, start=None, end=None, payed=True):
    return Transaction.objects.get_credit_balance(
      self.user,
      categories=[self],
      start=start,
      end=end,
      payed=payed)

  def get_debit_balance(self, start=None, end=None, payed=True):
    return Transaction.objects.get_debit_balance(
      self.user,
      categories=[self],
      start=start,
      end=end,
      payed=payed)


class BudgetManager(BaseManager):
  pass


class Budget(models.Model):
  TYPE_CREDIT = 1
  TYPE_DEBIT = 2
  TYPE_SAVINGS = 3
  TYPE = (
    (TYPE_DEBIT, 'Expenses'),
    (TYPE_CREDIT, 'Incomes'),
    (TYPE_SAVINGS, 'Investment'),)

  hashid = models.CharField(_('Hash'), max_length=255, null=True, blank=True, db_index=True)
  user = models.ForeignKey(User, verbose_name=_('User'))
  category = models.ForeignKey(Category, verbose_name=_('Category'), null=True, blank=True)
  type = models.PositiveIntegerField(_('Type'), choices=TYPE)
  date = models.DateField(_('Month'))
  amount = models.DecimalField(_('Amount'), max_digits=15, decimal_places=2,
                               validators=[MinValueValidator(Decimal('0.01'))])
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  objects = BudgetManager()

  class Meta:
    unique_together = ('category', 'date')
    index_together = (('user', 'category', 'date'),)

  _amount_complete = None

  def __str__(self):
    return '%s = $ %s' % (self.category.name, self.amount)

  @property
  def date_start(self):
    return self.date

  @property
  def date_end(self):
    return last_day(self.date)

  @property
  def percent_complete(self):
    return (self.amount_complete / self.amount) * 100

  @property
  def amount_complete(self):
    if self._amount_complete:
      return self._amount_complete
    if self.type == self.TYPE_DEBIT:
      # debits - credits
      self._amount_complete = (
        self.category.get_debit_balance(self.date_start, self.date_end) -
        self.category.get_credit_balance(self.date_start, self.date_end))
    elif self.type == self.TYPE_CREDIT:
      # credits - debits
      self._amount_complete = (
        self.category.get_credit_balance(self.date_start, self.date_end) -
        self.category.get_debit_balance(self.date_start, self.date_end))
    elif self.type == self.TYPE_SAVINGS:
      # sum of the balances of savings accounts
      accounts = Account.objects.get_queryset(self.user).filter(is_savings=True)
      self._amount_complete = sum(
        account.get_balance(self.date_start, self.date_end)
        for account in accounts)
    else:
      raise Exception(_('Tipo de meta inválido'))
    return self._amount_complete

  def save(self, **kwargs):
    self.date = first_day(self.date)
    return super().save(**kwargs)


class TransactionManager(BaseManager):
  def get_transactions(self, user, start=None, end=None, accounts=None,
                       categories=None, payed=None, type=None, description=None):
    """ Get a list of transactions """
    qs = self.get_queryset(user)
    if start:
      qs = qs.filter(date__gte=start)
    if end:
      qs = qs.filter(date__lte=end)
    if accounts:
      qs = qs.filter(account__in=accounts)
    if categories:
      qs = qs.filter(category__in=categories)
    if payed is not None:
      qs = qs.filter(payed=payed)
    if type:
      qs = qs.filter(type=type)
    if description:
      qs = qs.filter(description__icontains=description)
    return qs.select_related().order_by('date', '-pk')

  def get_credit_balance(self, user, start=None, end=None, accounts=None,
                         categories=None, payed=None, type=None, description=None):
    """ Calculate credit balance for transactions """
    qs = self.get_transactions(user, start, end, accounts, categories, payed, type, description)
    return qs.filter(type=Transaction.TYPE_CREDIT).aggregate(Sum('amount'))['amount__sum'] or 0

  def get_debit_balance(self, user, start=None, end=None, accounts=None,
                        categories=None, payed=None, type=None, description=None):
    """ Calculate debit balance for transactions """
    qs = self.get_transactions(user, start, end, accounts, categories, payed, type, description)
    return qs.filter(type=Transaction.TYPE_DEBIT).aggregate(Sum('amount'))['amount__sum'] or 0

  def get_balance(self, user, start=None, end=None, accounts=None,
                  categories=None, payed=None, type=None, description=None):
    """ Calculate the balance for transactions """
    credit = self.get_credit_balance(user, start, end, accounts,
                                     categories, payed, type, description)
    debit = self.get_debit_balance(user, start, end, accounts, categories, payed, type, description)
    return credit - debit

  def cash_flow(self, user, start, end, payed=None):
    """ Calculate expenses vs incomes for past period """
    result = []
    for date in month_range(first_day(start), last_day(end)):
      first = first_day(date)
      last = last_day(date)
      incomes = self.get_credit_balance(user, first, last, payed=payed)
      expenses = self.get_debit_balance(user, first, last, payed=payed)
      result.append({
        'date': date,
        'incomes': incomes,
        'expenses': expenses,
        'balance': incomes - expenses,
      })
    return result

  def cash_flow_by_day(self, user, start, end):
    """ Calculate the cash flow for each day in a period """
    trans = self.get_transactions(user, start, end).all()
    results = []
    for date in day_range(start, end):
      results.append({
        'date': date.date(),
        'incomes': sum(t.amount for t in trans
                       if t.type == Transaction.TYPE_CREDIT and t.date == date.date()) or 0,
        'expenses': sum(t.amount for t in trans
                        if t.type == Transaction.TYPE_DEBIT and t.date == date.date()) or 0
      })
    return results

  def cash_flow_by_category(self, user, start, end, payed=None):
    """ Calculate the cash flow for each category by month in period """
    trunc_date = connection.ops.date_trunc_sql('month', 'date')
    qs = self.get_queryset(user).extra({'month': trunc_date}).filter(date__gte=start, date__lte=end)
    if payed is not None:
      qs = qs.filter(payed=payed)
    qs = qs.values('category__name', 'month').annotate(Sum('amount'))

    credit = qs.filter(type=Transaction.TYPE_CREDIT).all()
    debit = qs.filter(type=Transaction.TYPE_DEBIT).all()

    credit_categories = set(c['category__name'] for c in credit)
    debit_categories = set(d['category__name'] for d in debit)
    range = list(month_range(start, end))

    credit_results = []
    debit_results = []
    total_credit_results = []
    total_debit_results = []

    for date in range:
      # credits
      for category in credit_categories:
        credit_results.append({
          'date': date,
          'category': category,
          'amount': [c['amount__sum'] for c in credit
                     if c['month'] == date and c['category__name'] == category] or [0]
        })
      total_credit_results.append({
        'date': date,
        'amount': sum(c['amount'][0] for c in credit_results
                      if c['date'] == date)
      })
      # debits
      for category in debit_categories:
        debit_results.append({
          'date': date,
          'category': category,
          'amount': [d['amount__sum'] for d in debit
                     if d['month'] == date and d['category__name'] == category] or [0]
        })
      total_debit_results.append({
        'date': date,
        'amount': sum(d['amount'][0] for d in debit_results
                      if d['date'] == date)
      })

    return {'month_range': range,
            'credit_categories': credit_categories,
            'debit_categories': debit_categories,
            'credit_results': credit_results,
            'debit_results': debit_results,
            'total_credit_results': total_credit_results,
            'total_debit_results': total_debit_results}


class Transaction(models.Model):
  TYPE_DEBIT = 1
  TYPE_CREDIT = 2
  TYPE_TRANSFER = 3
  TYPE = ((TYPE_DEBIT, _('Debit')),
          (TYPE_CREDIT, _('Credit')),
          (TYPE_TRANSFER, _('Transfer')))

  WEEKLY = 1
  BIWEEKLY = 2
  MONTHLY = 3
  BIMONTHLY = 4
  QUATERLY = 5
  BIANNUAL = 6
  ANNUAL = 7
  PERIOD = ((WEEKLY, _('Weekly')),
            (BIWEEKLY, _('Biweekly')),
            (MONTHLY, _('Monthly')),
            (BIMONTHLY, _('Bimonthly')),
            (QUATERLY, _('Quaterly')),
            (BIANNUAL, _('Biannual')),
            (ANNUAL, _('Annual')),)

  hashid = models.CharField(_('Hash'), max_length=255, null=True, blank=True, db_index=True)
  account = models.ForeignKey(Account, verbose_name=_('Account'))
  user = models.ForeignKey(User, verbose_name=_('User'))
  category = models.ForeignKey(Category, verbose_name=_('Category'))
  # every transaction that belongs to the same recurrence will have
  # the same recurrence key
  recurrence_key = models.CharField(max_length=255, blank=True, null=True, db_index=True)
  transfer_key = models.CharField(max_length=255, blank=True, null=True, db_index=True)
  installment_number = models.PositiveIntegerField(_('Installment'), default=1)
  installment_total = models.PositiveIntegerField(_('Total Installments'), default=1)
  date = models.DateField(_('Date'))
  description = models.TextField(_('Description'), null=True, blank=True)
  type = models.IntegerField(_('Type'), choices=TYPE, blank=False)
  amount = models.DecimalField(_('Amount'), max_digits=15, decimal_places=2,
                               validators=[MinValueValidator(Decimal('0.0'))])
  payed = models.BooleanField(_('Payed'), default=True, null=False, blank=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  objects = TransactionManager()

  def __str__(self):
    return self.hashid

  @property
  def is_credit(self):
    return self.type == Transaction.TYPE_CREDIT

  @property
  def is_debit(self):
    return self.type == Transaction.TYPE_DEBIT

  @property
  def is_transfer(self):
    return self.pk and self.category == Category.transfer_category(self.user)

  @property
  def recurrence_related(self):
    """ Find transactions that belong are recurrences """
    return Transaction.objects.get_queryset(self.user).filter(
      recurrence_key__isnull=False,
      recurrence_key=self.recurrence_key,
      account=self.account
    ).order_by('date')

  @property
  def transfer_related(self):
    """ Get the transaction related for a transfer """
    if not self.is_transfer:
      return None
    try:
      return Transaction.objects.select_related().exclude(
        pk=self.pk,
        transfer_key__isnull=False
      ).get(transfer_key=self.transfer_key)
    except (Transaction.DoesNotExist, Transaction.MultipleObjectsReturned):
      return None

  def save(self, *args, **kwargs):
    result = super().save(*args, **kwargs)
    if self.is_transfer:
      # also update the related transfer transaction
      # IMPORTANT: use update instead of save() to avoid infinite loop
      try:
        Transaction.objects.exclude(
          pk=self.pk,
          transfer_key__isnull=True
        ).filter(
          transfer_key=self.transfer_key
        ).update(
          description=self.description,
          amount=self.amount,
          date=self.date,
          payed=self.payed)
      except Transaction.DoesNotExist:
        pass
    return result

  @transaction.atomic
  def create_transaction(self, installments=None, period=None):
    """
    Create a new transaction
    :param self object with transaction data
    :param installments number of installments
    :param period period to generate the installments
    :returns the created transaction
    """
    dates = [self.date]
    if installments and period:
      period = int(period)
      if period == self.WEEKLY:
        dates = [d for d in week_range(self.date, count=installments)]
      elif period == self.BIWEEKLY:
        dates = [d for d in biweekly_range(self.date, count=installments)]
      elif period == self.MONTHLY:
        dates = [d for d in month_range(self.date, count=installments)]
      elif period == self.BIMONTHLY:
        dates = [d for d in bimonth_range(self.date, count=installments)]
      elif period == self.QUATERLY:
        dates = [d for d in quaterly_range(self.date, count=installments)]
      elif period == self.BIANNUAL:
        dates = [d for d in biannual_range(self.date, count=installments)]
      elif period == self.ANNUAL:
        dates = [d for d in annual_range(self.date, count=installments)]

    # is it a recurrence? if it is (more than one date) then we generate
    # a new recurrence key for the transactions
    installment_total = len(dates)
    is_recurrence = installment_total > 1
    recurrence_key = random_hashid() if is_recurrence else None
    payed = self.payed
    created_transactions = []

    for i, date in enumerate(dates, start=1):
      created_transactions.append(Transaction.objects.create(
        account=self.account,
        recurrence_key=recurrence_key,
        installment_number=i,
        installment_total=installment_total,
        category=self.category,
        user=self.user,
        date=date,
        description=self.description,
        amount=self.amount,
        type=self.type,
        payed=payed))
      # only the first recurrence should be payed
      payed = False

    return created_transactions

  @transaction.atomic
  def transfer(self, to_account):
    """ Create a transfer transaction between two accounts """
    # find the transfer category
    category = Category.transfer_category(self.user)
    transfer_key = random_hashid()

    # create the debit transaction
    t1 = Transaction.objects.create(
      account=self.account,
      category=category,
      user=self.user,
      date=self.date,
      amount=self.amount,
      type=Transaction.TYPE_DEBIT,
      transfer_key=transfer_key,
      description=self.description,
      payed=self.payed)

    # create the credit transaction
    t2 = Transaction.objects.create(
      account=to_account,
      category=category,
      user=self.user,
      date=self.date,
      amount=self.amount,
      type=Transaction.TYPE_CREDIT,
      transfer_key=transfer_key,
      description=self.description,
      payed=self.payed)

    return t1, t2


class WishListItemManager(BaseManager):
  pass


class WishListItem(models.Model):
  PRIORITIES = ((3, 'High'),
                (2, 'Medium'),
                (1, 'Low'))

  user = models.ForeignKey(User, verbose_name=_('User'))
  category = models.ForeignKey(Category, verbose_name=_('Category'),
                               blank=True, null=True)
  name = models.CharField(_('Name'), max_length=255)
  url = models.URLField(_('URL'), max_length=255, null=True, blank=True)
  purpose = models.TextField(_('Purpose'), blank=True, null=True)
  price = models.DecimalField(_('Price'), max_digits=15, decimal_places=2)
  priority = models.PositiveIntegerField(_('Priority'), choices=PRIORITIES)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  objects = WishListItemManager()

  def __str__(self):
    return self.name
