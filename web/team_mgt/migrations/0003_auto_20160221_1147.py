# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-21 11:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('team_mgt', '0002_auto_20160217_1145'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teamtaskhistory',
            old_name='action_taken_by',
            new_name='user',
        ),
    ]
