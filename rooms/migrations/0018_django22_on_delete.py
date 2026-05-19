# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('films', '0017_karaoke_packages_payments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeslot',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='films.Room'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='timeslot_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='films.TimeSlot'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='package',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='films.ServicePackage',
            ),
        ),
        migrations.AlterField(
            model_name='booking',
            name='timeslot_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='films.TimeSlot'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='package',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='films.ServicePackage',
            ),
        ),
        migrations.AlterField(
            model_name='payment',
            name='booking',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='payment',
                to='films.Booking',
            ),
        ),
        migrations.AlterField(
            model_name='bookingstat',
            name='timeslot_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='films.TimeSlot'),
        ),
    ]
