# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('printers', '0003_auto_20141222_0830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='printerlist',
            name='name',
            field=models.CharField(unique=True, max_length=200),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='subscriptionprinterlist',
            name='subnet',
            field=models.CharField(unique=True, max_length=200),
            preserve_default=True,
        ),
    ]
