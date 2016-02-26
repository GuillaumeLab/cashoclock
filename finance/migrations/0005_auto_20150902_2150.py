# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_budget_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='transfer_key',
            field=models.CharField(blank=True, null=True, db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='budget',
            name='amount',
            field=models.DecimalField(validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Valor', max_digits=15, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='budget',
            name='category',
            field=models.ForeignKey(verbose_name='Categoria', to='finance.Category'),
        ),
        migrations.AlterField(
            model_name='budget',
            name='type',
            field=models.PositiveIntegerField(verbose_name='Tipo', choices=[(2, 'Débito'), (1, 'Crédito')]),
        ),
    ]
