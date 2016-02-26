# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0010_auto_20151017_1948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wishlistitem',
            name='url',
            field=models.URLField(max_length=255, blank=True, null=True, verbose_name='URL'),
        ),
    ]
