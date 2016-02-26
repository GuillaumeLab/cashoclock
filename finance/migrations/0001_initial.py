# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('hashid', models.CharField(blank=True, db_index=True, verbose_name='Hash', null=True, max_length=255)),
                ('name', models.CharField(verbose_name='Nome', max_length=255)),
                ('description', models.TextField(blank=True, verbose_name='Descrição', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
        ),
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('hashid', models.CharField(blank=True, db_index=True, verbose_name='Hash', null=True, max_length=255)),
                ('date', models.DateField(verbose_name='Mês')),
                ('amount', models.DecimalField(max_digits=15, verbose_name='Valor', decimal_places=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('hashid', models.CharField(blank=True, db_index=True, verbose_name='Hash', null=True, max_length=255)),
                ('name', models.CharField(verbose_name='Nome', max_length=255)),
                ('color_hex', models.CharField(verbose_name='Cor', max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('hashid', models.CharField(blank=True, db_index=True, verbose_name='Hash', null=True, max_length=255)),
                ('recurrence_key', models.CharField(blank=True, db_index=True, null=True, max_length=255)),
                ('installment_number', models.PositiveIntegerField(default=1, verbose_name='Parcela')),
                ('installment_total', models.PositiveIntegerField(default=1, verbose_name='Total Parcelas')),
                ('date', models.DateField(verbose_name='Data')),
                ('description', models.TextField(blank=True, verbose_name='Descrição', null=True)),
                ('type', models.IntegerField(choices=[(1, 'Débito'), (2, 'Crédito')], verbose_name='Tipo')),
                ('amount', models.DecimalField(validators=[django.core.validators.MinValueValidator(Decimal('0.0'))], decimal_places=2, verbose_name='Valor', max_digits=15)),
                ('payed', models.BooleanField(default=True, verbose_name='Pago')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(to='finance.Account', verbose_name='Conta')),
                ('category', models.ForeignKey(to='finance.Category', verbose_name='Categoria')),
                ('transfer', models.ForeignKey(verbose_name='Transferência', to='finance.Transaction', blank=True, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
        ),
        migrations.AddField(
            model_name='budget',
            name='category',
            field=models.ForeignKey(to='finance.Category', verbose_name='Category'),
        ),
        migrations.AddField(
            model_name='budget',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Usuário'),
        ),
        migrations.AlterUniqueTogether(
            name='budget',
            unique_together=set([('category', 'date')]),
        ),
        migrations.AlterIndexTogether(
            name='budget',
            index_together=set([('user', 'category', 'date')]),
        ),
    ]
