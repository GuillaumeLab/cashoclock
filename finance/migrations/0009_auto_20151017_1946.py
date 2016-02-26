# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0008_wishlistitem_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='is_savings',
            field=models.BooleanField(verbose_name='Conta de Investimento?', default=False),
        ),
        migrations.AlterField(
            model_name='wishlistitem',
            name='priority',
            field=models.PositiveIntegerField(choices=[(3, 'Alta'), (2, 'Média'), (1, 'Baixa')], verbose_name='Prioridade'),
        ),
    ]
