from django.db import models
from django.forms import ValidationError

import datetime


# Create your models here.

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

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def room_type_get(self):
        a = ''
        for i in self.room_type.all():
            a += i.name + ','

        return a[:-1] if a else ''


class TimeSlot(models.Model):
    date = models.DateField()
    time = models.CharField(max_length=30)
    room = models.ForeignKey(Room)
    price = models.IntegerField()
    is_available = models.BooleanField(default=True)

    def __unicode__(self):
        name = str(self.room.name) + ", " + str(self.date) + " " + str(self.time)
        return name

    def __str__(self):
        name = str(self.room.name) + ", " + str(self.date) + " " + str(self.time)[:5]
        return name

    def room_name_get(self):
        return self.room.name

    def save(self, *args, **kwargs):
        for slot in TimeSlot.objects.filter(date=getattr(self, 'date'), room=getattr(self, 'room')):

            time1 = datetime.datetime.combine(
                getattr(self, 'date'),
                datetime.datetime.strptime(
                    getattr(self, 'time'),
                    '%H:%M').time()
            )
            time2 = datetime.datetime.now()

            if getattr(self, 'time') == slot.time or time1 < time2:
                raise ValidationError('Выбрано неподходящее время для бронирования.')

        super(TimeSlot, self).save(*args, **kwargs)


class Reservation(models.Model):
    timeslot_id = models.ForeignKey(TimeSlot)
    forname = models.CharField(max_length=20)
    persons_count = models.IntegerField(default=0)
    special_requests = models.TextField(blank=True)
    price = models.IntegerField(default=0)

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
    timeslot_id = models.ForeignKey(TimeSlot)
    persons_count = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    booking_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        booking_stat, created = BookingStat.objects.get_or_create(timeslot_id=getattr(self, 'timeslot_id'))
        booking_stat.total_bookings += 1
        booking_stat.total_sum += int(getattr(self, 'price'))
        booking_stat.save()

        super(Booking, self).save(*args, **kwargs)

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


class BookingStat(models.Model):
    timeslot_id = models.ForeignKey(TimeSlot)
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

