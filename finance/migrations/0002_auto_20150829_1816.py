# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transfer',
            field=models.ForeignKey(blank=True, verbose_name='Transferência', null=True, to='finance.Account', related_name='transfer'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.IntegerField(verbose_name='Tipo', choices=[(1, 'Débito'), (2, 'Crédito'), (3, 'Transferência')]),
        ),
    ]
