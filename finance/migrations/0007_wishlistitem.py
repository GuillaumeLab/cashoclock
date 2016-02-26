# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finance', '0006_remove_category_color_hex'),
    ]

    operations = [
        migrations.CreateModel(
            name='WishListItem',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Nome')),
                ('purpose', models.TextField(null=True, verbose_name='Propósito', blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Preço')),
                ('priority', models.PositiveIntegerField(choices=[(3, 'Alta'), (2, 'Normal'), (1, 'Baixa')], verbose_name='Prioridade')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(null=True, blank=True, to='finance.Category', verbose_name='Categoria')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
        ),
    ]
