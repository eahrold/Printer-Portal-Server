# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('printers', '0002_auto_20141221_2359'),
    ]

    operations = [
        migrations.RenameField(
            model_name='printer',
            old_name='option',
            new_name='options',
        ),
    ]
