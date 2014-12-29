# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sparkle', '0002_githubversion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='githubversion',
            name='last_checked',
            field=models.DateField(),
            preserve_default=True,
        ),
    ]
