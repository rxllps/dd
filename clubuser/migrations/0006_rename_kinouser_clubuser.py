# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kinouser', '0005_kinouser_is_staff'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Kinouser',
            new_name='ClubUser',
        ),
    ]
