# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0005_auto_20150902_2150'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='color_hex',
        ),
    ]
