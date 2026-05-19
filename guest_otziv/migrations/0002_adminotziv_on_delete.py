# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('guest_otziv', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminotziv',
            name='guestOtziv',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='guest_otziv.GuestOtziv',
            ),
        ),
    ]
