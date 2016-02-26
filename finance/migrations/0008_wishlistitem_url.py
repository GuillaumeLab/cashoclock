# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0007_wishlistitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlistitem',
            name='url',
            field=models.URLField(max_length=255, verbose_name='URL', default=''),
            preserve_default=False,
        ),
    ]
