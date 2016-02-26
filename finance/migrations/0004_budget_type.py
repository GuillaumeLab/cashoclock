# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_remove_transaction_transfer'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='type',
            field=models.PositiveIntegerField(verbose_name='Tipo', choices=[(1, 'Crédito'), (2, 'Débito')], default=1),
            preserve_default=False,
        ),
    ]
