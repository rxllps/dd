# -*- coding: utf-8 -*-
"""Платёжные провайдеры: mock для разработки и заготовка под ЮKassa."""

import uuid

from django.conf import settings
from django.utils import timezone

from rooms.models import Payment


class BasePaymentProvider(object):
    def create_payment(self, payment):
        raise NotImplementedError

    def confirm_payment(self, payment, external_id=None):
        raise NotImplementedError


class MockPaymentProvider(BasePaymentProvider):
    def create_payment(self, payment):
        payment.external_id = 'mock-%s' % uuid.uuid4().hex[:12]
        payment.payment_url = '/payment/%s/pay/' % payment.booking_id
        payment.save()
        return payment.payment_url

    def confirm_payment(self, payment, external_id=None):
        payment.status = Payment.STATUS_PAID
        payment.paid_at = timezone.now()
        if external_id:
            payment.external_id = external_id
        payment.save()
        payment.booking.mark_paid()
        return True


class YooKassaPaymentProvider(BasePaymentProvider):
    """Заготовка: при наличии YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY подключается API."""

    def create_payment(self, payment):
        shop_id = getattr(settings, 'YOOKASSA_SHOP_ID', '')
        secret = getattr(settings, 'YOOKASSA_SECRET_KEY', '')
        if not shop_id or not secret:
            return MockPaymentProvider().create_payment(payment)
        payment.external_id = 'yk-pending-%s' % payment.id
        payment.payment_url = '/payment/%s/pay/' % payment.booking_id
        payment.save()
        return payment.payment_url

    def confirm_payment(self, payment, external_id=None):
        payment.status = Payment.STATUS_PAID
        payment.paid_at = timezone.now()
        if external_id:
            payment.external_id = external_id
        payment.save()
        payment.booking.mark_paid()
        return True


def get_payment_provider():
    provider = getattr(settings, 'PAYMENT_PROVIDER', 'mock')
    if provider == 'yookassa':
        return YooKassaPaymentProvider()
    return MockPaymentProvider()
