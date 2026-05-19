# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('films', '0016_auto_20160521_1722'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServicePackage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('duration_hours', models.PositiveSmallIntegerField(default=1)),
                ('base_price', models.IntegerField()),
                ('includes', models.TextField(blank=True, help_text='Напитки, закуски, оборудование и т.д.')),
                ('discount_percent', models.PositiveSmallIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('room_types', models.ManyToManyField(blank=True, to='films.RoomType')),
            ],
        ),
        migrations.AddField(
            model_name='room',
            name='close_time',
            field=models.CharField(default='23:00', max_length=5),
        ),
        migrations.AddField(
            model_name='room',
            name='open_time',
            field=models.CharField(default='12:00', max_length=5),
        ),
        migrations.AddField(
            model_name='room',
            name='slot_step_minutes',
            field=models.PositiveSmallIntegerField(default=60, help_text='Шаг генерации слотов (минуты)'),
        ),
        migrations.AddField(
            model_name='timeslot',
            name='duration_minutes',
            field=models.PositiveSmallIntegerField(default=60),
        ),
        migrations.AddField(
            model_name='timeslot',
            name='status',
            field=models.CharField(
                choices=[
                    ('free', 'Свободен'),
                    ('reserved', 'Зарезервирован'),
                    ('paid', 'Оплачен'),
                    ('cancelled', 'Отменён'),
                ],
                default='free',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='booking',
            name='duration_hours',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='booking',
            name='payment_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Ожидает оплаты'),
                    ('paid', 'Оплачено'),
                    ('failed', 'Ошибка оплаты'),
                    ('refunded', 'Возврат'),
                    ('cancelled', 'Отменено'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='booking',
            name='special_requests',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='package',
            field=models.ForeignKey(blank=True, null=True, to='films.ServicePackage'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='duration_hours',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='reservation',
            name='package',
            field=models.ForeignKey(blank=True, null=True, to='films.ServicePackage'),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Ожидает'),
                        ('paid', 'Оплачен'),
                        ('failed', 'Ошибка'),
                        ('refunded', 'Возврат'),
                    ],
                    default='pending',
                    max_length=20,
                )),
                ('provider', models.CharField(default='mock', max_length=30)),
                ('external_id', models.CharField(blank=True, max_length=100)),
                ('payment_url', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('booking', models.OneToOneField(related_name='payment', to='films.Booking')),
            ],
        ),
    ]
