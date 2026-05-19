from django.db import models
from django.forms import ValidationError
import datetime


class RoomType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    url_name = models.CharField(max_length=50, unique=True)
    full_description = models.TextField()
    max_persons = models.IntegerField()
    equipment = models.TextField()
    price_per_hour = models.IntegerField()
    image = models.ImageField(
        upload_to="media/rooms",
        height_field="image_height",
        width_field="image_width"
    )
    image_height = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        default="525"
    )
    image_width = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        default="260"
    )
    video_url = models.URLField(blank=True, null=True)
    room_type = models.ManyToManyField(RoomType)
    is_available = models.BooleanField(default=True)
    slot_step_minutes = models.PositiveSmallIntegerField(
        default=60,
        help_text='Шаг генерации слотов (минуты)'
    )
    open_time = models.CharField(max_length=5, default='12:00')
    close_time = models.CharField(max_length=5, default='23:00')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def room_type_get(self):
        a = ''
        for i in self.room_type.all():
            a += i.name + ','
        return a[:-1] if a else ''


class ServicePackage(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration_hours = models.PositiveSmallIntegerField(default=1)
    base_price = models.IntegerField()
    includes = models.TextField(
        blank=True,
        help_text='Напитки, закуски, оборудование и т.д.'
    )
    room_types = models.ManyToManyField(RoomType, blank=True)
    discount_percent = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def applies_to_room(self, room):
        if not self.room_types.exists():
            return True
        return self.room_types.filter(id__in=room.room_type.values_list('id', flat=True)).exists()


class TimeSlot(models.Model):
    STATUS_FREE = 'free'
    STATUS_RESERVED = 'reserved'
    STATUS_PAID = 'paid'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = (
        (STATUS_FREE, 'Свободен'),
        (STATUS_RESERVED, 'Зарезервирован'),
        (STATUS_PAID, 'Оплачен'),
        (STATUS_CANCELLED, 'Отменён'),
    )

    date = models.DateField()
    time = models.CharField(max_length=30)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    price = models.IntegerField()
    duration_minutes = models.PositiveSmallIntegerField(default=60)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_FREE
    )
    is_available = models.BooleanField(default=True)

    def __unicode__(self):
        return str(self.room.name) + ", " + str(self.date) + " " + str(self.time)

    def __str__(self):
        return str(self.room.name) + ", " + str(self.date) + " " + str(self.time)[:5]

    def room_name_get(self):
        return self.room.name

    def is_bookable(self):
        return self.status == self.STATUS_FREE and self.is_available

    def reserve(self):
        self.status = self.STATUS_RESERVED
        self.is_available = False
        self.save()

    def mark_paid(self):
        self.status = self.STATUS_PAID
        self.is_available = False
        self.save()

    def release(self):
        self.status = self.STATUS_FREE
        self.is_available = True
        self.save()

    def cancel_slot(self):
        self.status = self.STATUS_CANCELLED
        self.is_available = False
        self.save()

    def save(self, *args, **kwargs):
        for slot in TimeSlot.objects.filter(date=getattr(self, 'date'), room=getattr(self, 'room')):
            if slot.pk == self.pk:
                continue
            time1 = datetime.datetime.combine(
                getattr(self, 'date'),
                datetime.datetime.strptime(getattr(self, 'time'), '%H:%M').time()
            )
            time2 = datetime.datetime.now()
            if getattr(self, 'time') == slot.time or time1 < time2:
                raise ValidationError('Выбрано неподходящее время для бронирования.')
        super(TimeSlot, self).save(*args, **kwargs)


class Reservation(models.Model):
    timeslot_id = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    forname = models.CharField(max_length=20)
    persons_count = models.IntegerField(default=0)
    special_requests = models.TextField(blank=True)
    price = models.IntegerField(default=0)
    package = models.ForeignKey(
        ServicePackage, null=True, blank=True, on_delete=models.SET_NULL
    )
    duration_hours = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __unicode__(self):
        return self.forname

    def __str__(self):
        return self.forname

    def room_name_get(self):
        return self.timeslot_id.room.name

    def reservation_date_get(self):
        return self.timeslot_id.date

    def reservation_time_get(self):
        return self.timeslot_id.time


class Booking(models.Model):
    PAYMENT_PENDING = 'pending'
    PAYMENT_PAID = 'paid'
    PAYMENT_FAILED = 'failed'
    PAYMENT_REFUNDED = 'refunded'
    PAYMENT_CANCELLED = 'cancelled'

    PAYMENT_STATUS_CHOICES = (
        (PAYMENT_PENDING, 'Ожидает оплаты'),
        (PAYMENT_PAID, 'Оплачено'),
        (PAYMENT_FAILED, 'Ошибка оплаты'),
        (PAYMENT_REFUNDED, 'Возврат'),
        (PAYMENT_CANCELLED, 'Отменено'),
    )

    timeslot_id = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    persons_count = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    booking_date = models.DateTimeField(auto_now_add=True)
    package = models.ForeignKey(
        ServicePackage, null=True, blank=True, on_delete=models.SET_NULL
    )
    duration_hours = models.PositiveSmallIntegerField(default=1)
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_PENDING
    )
    special_requests = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super(Booking, self).save(*args, **kwargs)
        if is_new and self.payment_status == self.PAYMENT_PAID:
            self._update_stats()

    def mark_paid(self):
        self.payment_status = self.PAYMENT_PAID
        self.save()
        self.timeslot_id.mark_paid()
        self._update_stats()

    def mark_cancelled(self, fee=0):
        self.payment_status = self.PAYMENT_CANCELLED
        self.save()
        self.timeslot_id.release()

    def _update_stats(self):
        booking_stat, created = BookingStat.objects.get_or_create(timeslot_id=self.timeslot_id)
        booking_stat.total_bookings += 1
        booking_stat.total_sum += int(self.price)
        booking_stat.save()

    def __unicode__(self):
        return str(self.id)

    def __str__(self):
        return str(self.id)

    def room_name_get(self):
        return self.timeslot_id.room.name

    def booking_date_get(self):
        return self.timeslot_id.date

    def booking_time_get(self):
        return self.timeslot_id.time


class Payment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Ожидает'),
        (STATUS_PAID, 'Оплачен'),
        (STATUS_FAILED, 'Ошибка'),
        (STATUS_REFUNDED, 'Возврат'),
    )

    PROVIDER_MOCK = 'mock'
    PROVIDER_YOOKASSA = 'yookassa'

    booking = models.OneToOneField(Booking, related_name='payment', on_delete=models.CASCADE)
    amount = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    provider = models.CharField(max_length=30, default=PROVIDER_MOCK)
    external_id = models.CharField(max_length=100, blank=True)
    payment_url = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return 'Payment #%s (%s)' % (self.id, self.status)


class BookingStat(models.Model):
    timeslot_id = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    total_bookings = models.IntegerField(default=0)
    total_sum = models.IntegerField(default=0)

    def __unicode__(self):
        return str(self.timeslot_id)

    def __str__(self):
        return str(self.timeslot_id)

    def get_room_name(self):
        return self.timeslot_id.room.name

    def get_booking_date(self):
        return self.timeslot_id.date

    def get_booking_time(self):
        return self.timeslot_id.time
