# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PrivateKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('private_key', models.FileField(upload_to=b'private/')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SystemProfileReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip_address', models.IPAddressField()),
                ('added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SystemProfileReportRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=80)),
                ('report', models.ForeignKey(to='sparkle.SystemProfileReport')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('version', models.CharField(max_length=10, null=True, blank=True)),
                ('short_version', models.CharField(max_length=50, null=True, blank=True)),
                ('dsa_signature', models.CharField(max_length=80, null=True, blank=True)),
                ('length', models.CharField(max_length=20, null=True, blank=True)),
                ('release_notes', models.TextField(null=True, blank=True)),
                ('minimum_system_version', models.CharField(max_length=10, null=True, blank=True)),
                ('published', models.DateTimeField(auto_now_add=True)),
                ('update', models.FileField(upload_to=b'sparkle/')),
                ('active', models.BooleanField(default=False)),
                ('application', models.ForeignKey(to='sparkle.Application')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
