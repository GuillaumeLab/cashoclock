# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_auto_20150829_1816'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='transfer',
        ),
    ]
