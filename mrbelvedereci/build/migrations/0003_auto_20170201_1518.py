# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-01 15:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cumulusci', '0002_scratchorginstance'),
        ('build', '0002_auto_20170117_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='build',
            name='org',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='builds', to='cumulusci.Org'),
        ),
        migrations.AddField(
            model_name='build',
            name='org_instance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='builds', to='cumulusci.ScratchOrgInstance'),
        ),
    ]