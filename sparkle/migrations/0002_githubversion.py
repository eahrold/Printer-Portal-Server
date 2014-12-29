# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sparkle', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GitHubVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField()),
                ('last_checked', models.DateField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
