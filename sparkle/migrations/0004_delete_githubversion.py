# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sparkle', '0003_auto_20141223_0044'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GitHubVersion',
        ),
    ]
