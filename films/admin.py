from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from films.models import *
import datetime


# Register your models here.

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'room_name_get', 'booking_date_get', 'booking_time_get', 'persons_count', 'price',)
    search_fields = ('timeslot_id__room__name',)
    list_filter = (
        ('timeslot_id__date', DateFieldListFilter),
    )


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'max_persons', 'price_per_hour', 'room_type_get', 'is_available',)
    search_fields = ('name', 'description', 'room_type__name')
    list_filter = ('is_available', 'room_type',)
    filter_horizontal = ('room_type',)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'date', 'time', 'price', 'is_available',)
    search_fields = ('room__name',)
    list_filter = (
        ('date', DateFieldListFilter),
        'is_available',
    )
    fieldsets = ((
        None, {
            'fields': ('date', 'time', 'room', 'price', 'is_available')
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room":
            kwargs["queryset"] = Room.objects.filter(is_available=True)
        return super(TimeSlotAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'room_name_get', 'reservation_date_get', 'reservation_time_get', 'forname', 'persons_count', 'price',)
    search_fields = ('forname', 'timeslot_id__room__name')
    list_filter = (
        ('timeslot_id__date', DateFieldListFilter),
    )


@admin.register(BookingStat)
class BookingStatAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_room_name', 'get_booking_date', 'get_booking_time', 'total_bookings', 'total_sum',)
    search_fields = ('timeslot_id__room__name',)
    list_filter = (
        ('timeslot_id__date', DateFieldListFilter),
    )
