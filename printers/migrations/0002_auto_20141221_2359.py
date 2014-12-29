# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('printers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='printer',
            name='option',
            field=models.ManyToManyField(to='printers.Option', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='printer',
            name='ppd_file',
            field=models.FileField(null=True, upload_to=b'ppds/', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='printer',
            name='protocol',
            field=models.CharField(default=b'ipp', max_length=200, choices=[(b'ipp', b'ipp'), (b'socket', b'socket'), (b'lpd', b'lpd'), (b'http', b'http')]),
            preserve_default=True,
        ),
    ]
