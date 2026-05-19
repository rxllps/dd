# -*- coding: utf-8 -*-
"""Расчёт стоимости бронирования: пакеты, выходные, групповые скидки."""

from datetime import datetime, timedelta

WEEKEND_SURCHARGE = 0.20
GROUP_HOURS_FOR_DISCOUNT = 5
GROUP_DISCOUNT = 0.15
CANCEL_FREE_HOURS = 2
CANCEL_FEE_RATE = 0.50


def is_weekend(booking_date):
    return booking_date.weekday() >= 5


def hours_until_slot(timeslot):
    slot_dt = datetime.combine(
        timeslot.date,
        datetime.strptime(timeslot.time, '%H:%M').time()
    )
    delta = slot_dt - datetime.now()
    return delta.total_seconds() / 3600.0


def cancellation_fee(amount, timeslot):
    if hours_until_slot(timeslot) >= CANCEL_FREE_HOURS:
        return 0
    return int(amount * CANCEL_FEE_RATE)


def calculate_booking_price(room, timeslot, package=None, duration_hours=1):
    if package:
        duration_hours = max(duration_hours, package.duration_hours)
        amount = float(package.base_price)
        if package.discount_percent:
            amount *= (100.0 - package.discount_percent) / 100.0
    else:
        hourly = timeslot.price or room.price_per_hour
        amount = float(hourly) * duration_hours

    if duration_hours >= GROUP_HOURS_FOR_DISCOUNT:
        amount *= (1.0 - GROUP_DISCOUNT)

    if is_weekend(timeslot.date):
        amount *= (1.0 + WEEKEND_SURCHARGE)

    return int(round(amount))
