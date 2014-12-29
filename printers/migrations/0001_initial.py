# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('option', models.CharField(unique=True, max_length=200, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Printer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200, blank=True)),
                ('host', models.CharField(max_length=200)),
                ('protocol', models.CharField(max_length=200)),
                ('location', models.CharField(max_length=200, blank=True)),
                ('model', models.CharField(max_length=200, blank=True)),
                ('ppd_file', models.FileField(upload_to=b'ppds/', blank=True)),
                ('option', models.ManyToManyField(to='printers.Option', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PrinterList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('public', models.BooleanField(default=True)),
                ('printer', models.ManyToManyField(to='printers.Printer', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubscriptionPrinterList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subnet', models.CharField(max_length=200)),
                ('printer', models.ManyToManyField(to='printers.Printer', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
