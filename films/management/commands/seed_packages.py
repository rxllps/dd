# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from films.models import RoomType, ServicePackage


class Command(BaseCommand):
    help = 'Создание демонстрационных пакетов услуг'

    def handle(self, *args, **options):
        vip, _ = RoomType.objects.get_or_create(name='VIP')
        standard, _ = RoomType.objects.get_or_create(name='Стандарт')

        packages = [
            {
                'name': 'Стандарт 1 час',
                'description': 'Аренда комнаты на 1 час',
                'duration_hours': 1,
                'base_price': 800,
                'includes': 'Микрофоны, базовый напиточный сет',
                'discount_percent': 0,
                'room_types': [standard],
            },
            {
                'name': 'VIP вечер',
                'description': 'VIP-комната на 2 часа',
                'duration_hours': 2,
                'base_price': 4500,
                'includes': 'Премиум бар, фрукты, приоритетное обслуживание',
                'discount_percent': 10,
                'room_types': [vip],
            },
            {
                'name': 'Корпоратив 5 часов',
                'description': 'Групповое бронирование со скидкой',
                'duration_hours': 5,
                'base_price': 3500,
                'includes': 'Комната любой категории, закуски, -15% уже в тарифе',
                'discount_percent': 15,
                'room_types': [],
            },
        ]

        for data in packages:
            room_types = data.pop('room_types')
            pkg, created = ServicePackage.objects.get_or_create(
                name=data['name'],
                defaults=data,
            )
            if room_types:
                pkg.room_types = room_types
            pkg.is_active = True
            pkg.save()
            self.stdout.write('%s: %s' % (data['name'], 'создан' if created else 'обновлён'))

        self.stdout.write(self.style.SUCCESS('Пакеты услуг готовы.'))
