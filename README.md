# Система онлайн-бронирования караоке-комнат

Веб-приложение для развлекательного клуба: бронирование комнат, пакеты услуг, оплата, личный кабинет и отчёты.

**Стек:** Python, Django 2.2+, SQLite, HTML/CSS, jQuery.

## Структура проекта

| Папка / модуль | Назначение |
|----------------|------------|
| `rooms/` | Комнаты, слоты, бронирования, пакеты, платежи |
| `clubuser/` | Пользователи клуба (`ClubUser`) |
| `otziv/` | Отзывы о комнатах |
| `guest_otziv/` | Гостевая книга |
| `templates/` | Шаблоны (`rooms_home.html`, `room_schedule.html`, …) |
| `untitled/` | Настройки и маршруты Django |

> В БД сохранены технические метки приложений `films` и `kinouser` (для совместимости миграций). В коде используются папки `rooms` и `clubuser`.

## Быстрый старт

```bash
cd Documents/GitHub/Cinema
pip install django==2.2 reportlab pillow
python manage.py migrate
python manage.py seed_packages
python manage.py generate_timeslots --days 14
python manage.py createsuperuser
python manage.py runserver
```

Сайт: http://127.0.0.1:8000/

## Основные страницы

- `/` — расписание комнат
- `/room/<url_name>/` — слоты комнаты
- `/upcoming/` — каталог комнат
- `/price/` — тарифы и пакеты
- `/my_karaoke/` — о клубе
- `/cabinet/` — личный кабинет
- `/admin/` — управление
