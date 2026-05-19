from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from rooms.models import (
    RoomType, Room, TimeSlot, Booking, Reservation,
    BookingStat, ServicePackage, Payment,
)


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'duration_hours', 'base_price',
        'discount_percent', 'is_active',
    )
    list_filter = ('is_active', 'room_types')
    filter_horizontal = ('room_types',)
    search_fields = ('name',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'booking', 'amount', 'status',
        'provider', 'external_id', 'created_at', 'paid_at',
    )
    list_filter = ('status', 'provider', 'created_at')
    search_fields = ('external_id', 'booking__id')
    readonly_fields = ('created_at', 'paid_at')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'room_name_get', 'booking_date_get', 'booking_time_get',
        'persons_count', 'duration_hours', 'price', 'payment_status', 'package',
    )
    search_fields = ('timeslot_id__room__name',)
    list_filter = (
        'payment_status',
        ('timeslot_id__date', DateFieldListFilter),
    )


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'description', 'max_persons', 'price_per_hour',
        'room_type_get', 'is_available', 'open_time', 'close_time',
    )
    search_fields = ('name', 'description', 'room_type__name')
    list_filter = ('is_available', 'room_type',)
    filter_horizontal = ('room_type',)
    fieldsets = (
        (None, {
            'fields': (
                'name', 'description', 'url_name', 'full_description',
                'max_persons', 'equipment', 'price_per_hour', 'image',
                'video_url', 'room_type', 'is_available',
            )
        }),
        ('Расписание слотов', {
            'fields': ('open_time', 'close_time', 'slot_step_minutes'),
        }),
    )


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'room', 'date', 'time', 'price',
        'duration_minutes', 'status', 'is_available',
    )
    search_fields = ('room__name',)
    list_filter = (
        ('date', DateFieldListFilter),
        'status',
        'is_available',
    )
    actions = ['mark_free', 'mark_cancelled']

    def mark_free(self, request, queryset):
        for slot in queryset:
            slot.release()
    mark_free.short_description = 'Освободить выбранные слоты'

    def mark_cancelled(self, request, queryset):
        for slot in queryset:
            slot.cancel_slot()
    mark_cancelled.short_description = 'Отменить выбранные слоты'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room":
            kwargs["queryset"] = Room.objects.filter(is_available=True)
        return super(TimeSlotAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'room_name_get', 'reservation_date_get',
        'reservation_time_get', 'forname', 'persons_count',
        'price', 'package', 'duration_hours',
    )
    search_fields = ('forname', 'timeslot_id__room__name')
    list_filter = (
        ('timeslot_id__date', DateFieldListFilter),
    )


@admin.register(BookingStat)
class BookingStatAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_room_name', 'get_booking_date',
        'get_booking_time', 'total_bookings', 'total_sum',
    )
    search_fields = ('timeslot_id__room__name',)
    list_filter = (
        ('timeslot_id__date', DateFieldListFilter),
    )
