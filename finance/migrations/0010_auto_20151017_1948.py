# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0009_auto_20151017_1946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='category',
            field=models.ForeignKey(blank=True, null=True, to='finance.Category', verbose_name='Categoria'),
        ),
        migrations.AlterField(
            model_name='budget',
            name='type',
            field=models.PositiveIntegerField(verbose_name='Tipo', choices=[(2, 'Débito'), (1, 'Crédito'), (3, 'Investimento')]),
        ),
    ]
