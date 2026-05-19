# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from films.models import Room, TimeSlot


class Command(BaseCommand):
    help = 'Генерация временных слотов для комнат на N дней вперёд'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=14, help='Количество дней')
        parser.add_argument('--room', type=str, default='', help='url_name комнаты (все, если пусто)')

    def handle(self, *args, **options):
        days = options['days']
        room_filter = options['room']
        rooms = Room.objects.filter(is_available=True)
        if room_filter:
            rooms = rooms.filter(url_name=room_filter)

        created = 0
        for room in rooms:
            for day_offset in range(days):
                slot_date = datetime.now().date() + timedelta(days=day_offset)
                start = datetime.strptime(room.open_time, '%H:%M')
                end = datetime.strptime(room.close_time, '%H:%M')
                step = timedelta(minutes=room.slot_step_minutes)
                current = start
                while current < end:
                    time_str = current.strftime('%H:%M')
                    exists = TimeSlot.objects.filter(
                        room=room, date=slot_date, time=time_str
                    ).exists()
                    if not exists:
                        TimeSlot.objects.create(
                            room=room,
                            date=slot_date,
                            time=time_str,
                            price=room.price_per_hour,
                            duration_minutes=room.slot_step_minutes,
                            status=TimeSlot.STATUS_FREE,
                            is_available=True,
                        )
                        created += 1
                    current += step

        self.stdout.write(self.style.SUCCESS('Создано слотов: %s' % created))
