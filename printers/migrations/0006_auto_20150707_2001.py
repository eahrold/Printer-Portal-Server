# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('printers', '0005_auto_20150624_0102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='printer',
            name='protocol',
            field=models.CharField(default=b'ipp', max_length=200, choices=[(b'ipp', b'ipp'), (b'ipps', b'ipps'), (b'http', b'http'), (b'https', b'https'), (b'socket', b'socket'), (b'lpd', b'lpd')]),
            preserve_default=True,
        ),
    ]
