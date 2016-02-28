# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-17 05:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contractor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('created_by', models.CharField(default='System', editable=False, max_length=100)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified_by', models.CharField(default='System', editable=False, max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('remarks', models.TextField()),
                ('profile', models.TextField()),
                ('short_hand', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContractorContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('created_by', models.CharField(default='System', editable=False, max_length=100)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified_by', models.CharField(default='System', editable=False, max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('position', models.CharField(max_length=100)),
                ('eadd', models.CharField(max_length=100)),
                ('mobile_no', models.CharField(max_length=100)),
                ('office_no', models.CharField(max_length=100)),
                ('fax_no', models.CharField(max_length=100)),
                ('contractor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contract_mgt.Contractor')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
