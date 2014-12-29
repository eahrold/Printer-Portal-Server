# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('printers', '0004_auto_20141223_0821'),
    ]

    operations = [
        migrations.RenameField(
            model_name='printerlist',
            old_name='printer',
            new_name='printers',
        ),
        migrations.RenameField(
            model_name='subscriptionprinterlist',
            old_name='printer',
            new_name='printers',
        ),
    ]
