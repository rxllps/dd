from django.shortcuts import render_to_response, redirect, HttpResponse, render
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.paginator import Paginator
from django.contrib import auth
from django.conf import settings

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
from datetime import datetime, timedelta

from django.db import transaction

from rooms.models import (
    Room, TimeSlot, Booking, Reservation, BookingStat,
    ServicePackage, Payment,
)
from rooms import pricing
from rooms.payments import get_payment_provider
from clubuser.models import ClubUser
from guest_otziv.models import GuestOtziv, AdminOtziv
from otziv.models import Otziv
from .forms import UserCreateForm


def contact(request):
    args = dict()
    args['user'] = request.user
    return render_to_response('contact.html', args)


@csrf_protect
def guest(request):
    args = dict()
    args['user'] = request.user
    all_otzivs = otzivs = []

    for otziv_ in GuestOtziv.objects.all():
        otzivs.append(otziv_)
        try:
            otzivs.append(AdminOtziv.objects.get(guestOtziv=otziv_))
        except AdminOtziv.DoesNotExist:
            pass

        all_otzivs.append(otzivs.copy())
        otzivs.clear()
    args['otzivs'] = all_otzivs

    if request.POST:
        if request.POST.get('admin', '') == 'false':
            GuestOtziv(name=request.POST.get('name', ''), email=request.POST.get('email', ''),
                       text=request.POST.get('comment', ''), date=datetime.now().date()).save()
        elif request.POST.get('admin', '') == 'true':
            AdminOtziv(
                text=request.POST.get('comment', ''),
                guestOtziv=GuestOtziv.objects.get(id=request.POST.get('guest_id', ''))
            ).save()

        return redirect('/guest/')

    return render(request, 'guest.html', args)


def logout(request):
    auth.logout(request)
    return redirect("/")


@csrf_protect
def login(request):
    args = dict()
    if request.POST:
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(email=email, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            args['user'] = request.user

            return redirect("/")
        else:
            args['login_error'] = "Некорректные данные для входа"
            return render(request, 'signin.html', args)
    else:
        return render(request, 'signin.html', args)


@csrf_protect
def register(request):
    args = dict()
    args['form'] = UserCreateForm()
    if request.POST:
        newuser_form = UserCreateForm(request.POST)
        if newuser_form.is_valid():
            newuser_form.save()
            newuser = auth.authenticate(username=newuser_form.cleaned_data['email'],
                                        password=newuser_form.cleaned_data['password2'])
            auth.login(request, newuser)

            return redirect('/')

        else:
            args['reg_error'] = 'Ошибка при регистрации.'
            args['form'] = newuser_form
    return render(request, 'registr.html', args)


def main(request, url_date=datetime.today().date(), page_number=1):
    tmp_args, tmp_args2 = dict(), dict()

    tmp_args['Понедельник'] = tmp_args2['Pon'] = 1
    tmp_args['Вторник'] = tmp_args2['Vt'] = 2
    tmp_args['Среда'] = tmp_args2['Sr'] = 3
    tmp_args['Четверг'] = tmp_args2['Cht'] = 4
    tmp_args['Пятница'] = tmp_args2['Pyat'] = 5
    tmp_args['Суббота'] = tmp_args2['Sub'] = 6
    tmp_args['Воскресенье'] = tmp_args2['Voskr'] = 7

    dates_for_weekday = dates = []
    dates.append((datetime.today().date().strftime('%Y-%m-%d'), 
                  datetime.isoweekday(datetime.today().date())))
    dates_for_weekday.append((datetime.today().date().strftime('%d.%m'), 
                              datetime.isoweekday(datetime.today().date())))

    for i in range(1, 7):
        dates_for_weekday.append(
            ((datetime.today().date() + timedelta(days=i)).strftime('%d.%m'),
             datetime.isoweekday((datetime.today().date() + timedelta(days=i)))))
        dates.append(
            ((datetime.today().date() + timedelta(days=i)).strftime('%Y-%m-%d'),
             datetime.isoweekday((datetime.today().date() + timedelta(days=i)))))

    def reverse_dictionary(dictionary):
        new_dictionary = dict()

        for key in dictionary:
            new_dictionary.setdefault(dictionary[key], key)
        return new_dictionary

    def fill_dates(_args, second_args, _dates):
        new_args = reverse_dictionary(_args)
        new_second_args = reverse_dictionary(second_args)
        for one_date in range(len(_dates)):
            _args[new_args[_dates[one_date][1]]] = _dates[one_date][0]
            second_args[new_second_args[_dates[one_date][1]]] = _dates[one_date][0]
        return _args, second_args

    args, args2 = fill_dates(tmp_args, tmp_args2, dates)

    args.update(args2)
    args['user'] = request.user
    args['date_url'] = str(url_date)
    args['for_date'] = datetime.strptime(str(url_date), '%Y-%m-%d').date()
    if isinstance(url_date, str):
        args['weekday'] = datetime.isoweekday(datetime.strptime(url_date, '%Y-%m-%d').date())
    else:
        args['weekday'] = datetime.isoweekday(url_date)
    timeslots = TimeSlot.objects.filter(date=str(url_date))
    a = b = []

    for slot in timeslots:
        if slot.room not in a:
            a.append(slot.room)
            b.append(slot)

    current_page = Paginator(b, 3)
    args['timeslots'] = current_page.page(page_number)
    if len(b) == 0:
        args['no_timeslots'] = True
    return render_to_response('rooms_home.html', args)


def mykaraoke(request):
    args = dict()
    args['user'] = request.user
    return render_to_response('about_karaoke.html', args)


def price(request):
    args = dict()
    args['user'] = request.user
    args['packages'] = ServicePackage.objects.filter(is_active=True)
    return render_to_response('price.html', args)


def room_detail(request, name=''):
    args = dict()
    timeslots_data = {}
    args['user'] = request.user
    room = TimeSlot.objects.filter(room__url_name=name)

    if room:
        timeslots = TimeSlot.objects.filter(
            room__url_name=name,
            date__gt=(datetime.today().date() - timedelta(days=1)),
            status=TimeSlot.STATUS_FREE,
            is_available=True,
        )
        args['timeslots'] = timeslots

        a = 0
        for i in range(10):
            date = datetime.today().date() + timedelta(days=a)
            a += 1
            day_slots = TimeSlot.objects.filter(
                room__url_name=name,
                date=date,
                status=TimeSlot.STATUS_FREE,
                is_available=True,
            )
            if day_slots.exists():
                timeslots_data[str(date)] = []
                for ts in day_slots:
                    if ts.date >= datetime.today().date():
                        timeslots_data[str(date)].append('Время: ' + str(ts.time))
                        timeslots_data[str(date)].append(ts.price)
                        timeslots_data[str(date)].append('slot_id=' + str(ts.id))

        args['room'] = Room.objects.filter(url_name=name)[0]
        args['timeslots_data'] = timeslots_data

        return render_to_response('room_schedule.html', args)

    return redirect('/')


def _get_package(package_id):
    if not package_id:
        return None
    try:
        return ServicePackage.objects.get(id=package_id, is_active=True)
    except ServicePackage.DoesNotExist:
        return None


def _parse_booking_form(request, slot):
    persons = int(request.POST.get('persons', '1') or 1)
    duration_hours = int(request.POST.get('duration_hours', '1') or 1)
    package = _get_package(request.POST.get('package_id', ''))
    special_requests = request.POST.get('special_requests', '')

    if persons > slot.room.max_persons:
        return None, 'Превышена вместимость комнаты (%s чел.)' % slot.room.max_persons

    if package and not package.applies_to_room(slot.room):
        return None, 'Пакет не подходит для выбранной комнаты'

    amount = pricing.calculate_booking_price(
        slot.room, slot, package=package, duration_hours=duration_hours
    )
    return {
        'persons': persons,
        'duration_hours': duration_hours,
        'package': package,
        'special_requests': special_requests,
        'amount': amount,
    }, None


@csrf_exempt
def booking_quote(request):
    if request.method != 'POST':
        return HttpResponse('method not allowed', status=405)
    try:
        slot = TimeSlot.objects.get(id=request.POST.get('slot_id', ''))
    except TimeSlot.DoesNotExist:
        return HttpResponse('slot not found', status=404)
    data, error = _parse_booking_form(request, slot)
    if error:
        return HttpResponse(error, status=400)
    return HttpResponse(str(data['amount']), content_type='text/plain')


@csrf_exempt
def booking(request, slot_id):
    args = dict()
    if request.method == 'POST':
        if not request.user.is_authenticated():
            return HttpResponse('auth required', status=403)

        user = request.user
        try:
            slot = TimeSlot.objects.get(id=request.POST.get('slot_id', ''))
        except TimeSlot.DoesNotExist:
            return HttpResponse('slot not found', status=404)

        if not slot.is_bookable():
            return HttpResponse('slot unavailable', status=409)

        data, error = _parse_booking_form(request, slot)
        if error:
            return HttpResponse(error, status=400)

        action = request.POST.get('action', '')

        if action == 'reserve':
            with transaction.atomic():
                slot = TimeSlot.objects.select_for_update().get(pk=slot.pk)
                if not slot.is_bookable():
                    return HttpResponse('slot unavailable', status=409)
                name_user = user.firstname + " " + user.lastname
                reservation = Reservation(
                    timeslot_id=slot,
                    forname=name_user,
                    persons_count=data['persons'],
                    price=data['amount'],
                    package=data['package'],
                    duration_hours=data['duration_hours'],
                    special_requests=data['special_requests'],
                )
                reservation.save()
                slot.reserve()
                user.reservations.add(reservation)
            return HttpResponse('ok', content_type='text/html')

        elif action == 'book':
            with transaction.atomic():
                slot = TimeSlot.objects.select_for_update().get(pk=slot.pk)
                if not slot.is_bookable():
                    return HttpResponse('slot unavailable', status=409)
                booking_obj = Booking(
                    timeslot_id=slot,
                    persons_count=data['persons'],
                    price=data['amount'],
                    package=data['package'],
                    duration_hours=data['duration_hours'],
                    special_requests=data['special_requests'],
                    payment_status=Booking.PAYMENT_PENDING,
                )
                booking_obj.save()
                slot.reserve()
                user.bookings.add(booking_obj)
                payment = Payment.objects.create(
                    booking=booking_obj,
                    amount=data['amount'],
                    provider=settings.PAYMENT_PROVIDER,
                )
                get_payment_provider().create_payment(payment)

            return HttpResponse('/payment/%s/' % booking_obj.id, content_type='text/plain')

        return HttpResponse('unknown action', status=400)

    else:
        try:
            slot = TimeSlot.objects.get(id=slot_id)
        except TimeSlot.DoesNotExist:
            return redirect('/')

        if not slot.is_bookable():
            return HttpResponse('Слот недоступен для бронирования', status=409)

        packages = ServicePackage.objects.filter(is_active=True)
        applicable = [p for p in packages if p.applies_to_room(slot.room)]

        args['user'] = request.user
        args['slot'] = slot
        args['room'] = slot.room
        args['packages'] = applicable
        args['price'] = pricing.calculate_booking_price(slot.room, slot)
        args['max_persons'] = slot.room.max_persons
        if request.user.is_authenticated():
            args['user_name'] = request.user.firstname + " " + request.user.lastname

        return render(request, 'buy_window.html', args)


def payment_page(request, booking_id):
    if not request.user.is_authenticated():
        return redirect('/sign_in/')
    try:
        booking_obj = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return redirect('/cabinet/')

    if booking_obj not in request.user.bookings.all():
        return redirect('/cabinet/')

    payment = getattr(booking_obj, 'payment', None)
    args = {
        'user': request.user,
        'booking': booking_obj,
        'payment': payment,
        'slot': booking_obj.timeslot_id,
        'room': booking_obj.timeslot_id.room,
    }
    return render(request, 'payment.html', args)


@csrf_exempt
def payment_confirm(request, booking_id):
    if request.method != 'POST':
        return redirect('/payment/%s/' % booking_id)

    if not request.user.is_authenticated():
        return redirect('/sign_in/')

    try:
        booking_obj = Booking.objects.get(id=booking_id)
        payment = booking_obj.payment
    except (Booking.DoesNotExist, Payment.DoesNotExist):
        return redirect('/cabinet/')

    if booking_obj not in request.user.bookings.all():
        return redirect('/cabinet/')

    if payment.status == Payment.STATUS_PAID:
        return redirect('/payment/%s/success/' % booking_id)

    provider = get_payment_provider()
    provider.confirm_payment(payment, external_id=request.POST.get('external_id', ''))
    return redirect('/payment/%s/success/' % booking_id)


def payment_success(request, booking_id):
    if not request.user.is_authenticated():
        return redirect('/sign_in/')
    try:
        booking_obj = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return redirect('/cabinet/')
    return render(request, 'payment_result.html', {
        'user': request.user,
        'booking': booking_obj,
        'payment': getattr(booking_obj, 'payment', None),
    })


@csrf_exempt
def payment_webhook(request):
    """Webhook для внешнего платёжного провайдера (заглушка)."""
    external_id = request.POST.get('external_id', '')
    booking_id = request.POST.get('booking_id', '')
    if not booking_id:
        return HttpResponse('bad request', status=400)
    try:
        payment = Payment.objects.get(booking_id=booking_id)
    except Payment.DoesNotExist:
        return HttpResponse('not found', status=404)
    get_payment_provider().confirm_payment(payment, external_id=external_id)
    return HttpResponse('ok')


def cancel_booking(request, booking_id):
    if not request.user.is_authenticated():
        return redirect('/sign_in/')
    try:
        booking_obj = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return redirect('/cabinet/')

    if booking_obj not in request.user.bookings.all() and not request.user.is_superuser:
        return redirect('/cabinet/')

    fee = pricing.cancellation_fee(booking_obj.price, booking_obj.timeslot_id)
    if request.method == 'POST':
        booking_obj.mark_cancelled(fee=fee)
        if hasattr(booking_obj, 'payment') and booking_obj.payment.status == Payment.STATUS_PAID:
            booking_obj.payment.status = Payment.STATUS_REFUNDED
            booking_obj.payment.save()
        return redirect('/cabinet/')

    return render(request, 'cancel_booking.html', {
        'user': request.user,
        'booking': booking_obj,
        'fee': fee,
        'free_hours': pricing.CANCEL_FREE_HOURS,
    })


def upcoming_rooms(request, page_number=1):
    args = dict()
    args['user'] = request.user

    rooms = Room.objects.filter(is_available=True)
    current_page = Paginator(rooms, 3)
    args['rooms'] = current_page.page(page_number)

    return render_to_response('soon.html', args)


def room_video(request, name=''):
    args = dict()
    args['user'] = request.user

    room = Room.objects.filter(url_name=name)
    if room:
        args['rooms'] = room
        args['room'] = room[0]
        return render_to_response('room_video_page.html', args)

    return redirect('/')


@csrf_protect
def room_review(request, name=''):
    args = dict()
    args['user'] = request.user
    args['room'] = Room.objects.filter(url_name=name)[0]
    args['comments'] = Otziv.objects.filter(room__url_name=name)
    if request.method == 'POST':
        Otziv(name=request.POST.get('name', ''), 
              email=request.POST.get('email', ''),
              text=request.POST.get('comment', ''), 
              room=Room.objects.get(url_name=name),
              date=datetime.now().date()).save()

        return render(request, 'otziv.html', args)
    else:
        if Room.objects.filter(url_name=name):
            return render(request, 'otziv.html', args)

    return redirect('/')


def create_booking_receipt(booking):
    c = canvas.Canvas(settings.MEDIA_ROOT + "booking_receipt.pdf", pagesize=(607, 265))

    receipt_bg = "static/img/booking_receipt.png"
    if not os.path.isfile(receipt_bg):
        receipt_bg = "static/img/bilet.png"
    c.drawImage(image=receipt_bg, x=0, y=0)
    pdfmetrics.registerFont(TTFont('font', 'Arial.TTF'))
    pdfmetrics.registerFont(TTFont('test', 'static/fonts/BuxtonSketch.ttf'))
    c.setFont("font", 20)
    c.drawString(130, 170, 'Количество человек:')
    c.drawString(360, 170, str(booking.persons_count))
    c.setFont("test", 28)
    c.drawString(130, 230, booking.timeslot_id.room.name)
    c.setFont("font", 21)
    c.drawString(130, 120, str(booking.timeslot_id.date))
    c.drawString(350, 120, booking.timeslot_id.time)
    c.setFont("font", 25)
    c.drawString(30, 50, 'Цена: ' + str(booking.price) + ' руб.')
    if booking.package:
        c.setFont("font", 16)
        c.drawString(30, 25, 'Пакет: ' + booking.package.name)
    c.setFont("font", 20)
    c.drawString(520, 230, str(booking.id))

    c.showPage()

    c.save()


def print_booking(request):
    admin = 'booking_true'
    try:
        booking = Booking.objects.get(id=request.POST.get('id_booking', ''))
        create_booking_receipt(booking)
    except Exception as e:
        print(e)
        admin = 'booking_false'

    return karaoke_cabinet(request, admin=admin)


def karaoke_cabinet(request, page_number=1, admin='0'):
    args = dict()

    user = request.user
    args['user'] = user
    args['admin'] = admin

    if not request.user.is_authenticated():
        return redirect('/')
    else:
        if not request.user.is_superuser:

            dates = []
            for booking in user.bookings.all():
                dates.append(TimeSlot.objects.get(id=booking.timeslot_id.id).date)

            for reservation in user.reservations.all():
                dates.append(TimeSlot.objects.get(id=reservation.timeslot_id.id).date)
            dates.sort()
            dates.reverse()
            items = []

            for date in dates:
                for booking in user.bookings.all():
                    if booking.timeslot_id.date == date:
                        if booking not in items:
                            items.append(booking)
                for reservation in user.reservations.all():
                    if reservation.timeslot_id.date == date:
                        if reservation in items:
                            pass
                        else:
                            items.append(reservation)

            current_page = Paginator(items, 6)
            args['items'] = current_page.page(page_number)

        else:
            if admin == 'booking_true':
                args['user_name'] = ClubUser.objects.get(
                    bookings=Booking.objects.get(id=request.POST.get('id_booking', ''))).lastname
                args['room_name'] = Booking.objects.get(id=request.POST.get('id_booking', '')).timeslot_id.room.name

            elif admin == 'booking_false':
                args['error'] = 'Данного бронирования не существует. Проверьте правильность кода.'

            elif admin == 'slot_true':
                my_slot = TimeSlot.objects.get(id=request.POST.get('id_slot', ''))
                args['slot_date'] = my_slot.date
                args['room_name'] = my_slot.room.name
                args['slot_time'] = my_slot.time

            elif admin == 'slot_false':
                args['slot_false'] = 'На данный слот еще нет бронирований.'

            elif admin == 'date_null' or admin == 'date_false':
                args['date_error'] = 'На данный день нет бронирований.'

    return render_to_response('kabinet.html', args)


def print_report(request, report_type):
    if report_type == 'slot':
        admin = 'slot_true'
        try:
            stats = [BookingStat.objects.get(timeslot_id=request.POST.get('id_slot', ''))]
            create_report(stats, 'slot')
        except Exception as e:
            print(e)
            admin = 'slot_false'

        return karaoke_cabinet(request, admin=admin)

    elif report_type == 'date':
        admin = 'date_true'
        try:
            stats = BookingStat.objects.filter(timeslot_id__date=request.POST.get('date_slot', ''))
            if stats.count() > 0:
                create_report(stats, 'date')
            else:
                admin = 'date_null'
        except Exception as e:
            print(e)
            admin = 'date_false'

        return karaoke_cabinet(request, admin=admin)

    elif report_type == 'interval':
        admin = 'interval_true'
        try:
            stats = BookingStat.objects.filter(
                timeslot_id__date__range=[request.POST.get('date1_slot', ''), 
                                          request.POST.get('date2_slot', '')])
            create_report(stats, 'interval')
        except Exception as e:
            print(e)
            admin = 'interval_false'

        return karaoke_cabinet(request, admin=admin)

    elif report_type == 'week':
        admin = 'week_true'
        try:
            today = datetime.now().date()
            week = datetime.today().date() - timedelta(days=7)
            stats = BookingStat.objects.filter(timeslot_id__date__range=[week, today])

            create_report(stats, 'week')
        except Exception as e:
            print(e)
            admin = 'week_false'

        return karaoke_cabinet(request, admin=admin)

    elif report_type == 'month':
        admin = 'month_true'
        try:
            today = datetime.now().date()
            month = datetime.today().date() - timedelta(days=30)
            stats = BookingStat.objects.filter(timeslot_id__date__range=[month, today])

            create_report(stats, 'month')
        except Exception as e:
            print(e)
            admin = 'month_false'

        return karaoke_cabinet(request, admin=admin)

    elif report_type == 'halfyear':
        admin = 'half_true'
        try:
            today = datetime.now().date()
            halfyear = datetime.today().date() - timedelta(days=180)
            stats = BookingStat.objects.filter(timeslot_id__date__range=[halfyear, today])
            create_report(stats, 'halfyear')
        except Exception as e:
            print(e)
            admin = 'half_false'

        return karaoke_cabinet(request, admin=admin)
    return karaoke_cabinet(request)


def create_report(stats, report_type):
    c = canvas.Canvas(settings.MEDIA_ROOT + "report.pdf")
    pdfmetrics.registerFont(TTFont('font', 'Arial.TTF'))
    pdfmetrics.registerFont(TTFont('test', 'static/fonts/BuxtonSketch.ttf'))
    c.setFont("test", 20)

    if report_type == 'slot':
        c.drawString(130, 800, 'Отчет по бронированиям караоке по временному слоту')
    elif report_type == 'date':
        c.drawString(130, 800, 'Отчет по бронированиям караоке по дате')
    elif report_type == 'interval':
        c.drawString(130, 800, 'Отчет по бронированиям караоке по датам')
    elif report_type == 'week':
        c.drawString(130, 800, 'Отчет по бронированиям караоке за неделю')
    elif report_type == 'month':
        c.drawString(130, 800, 'Отчет по бронированиям караоке за месяц')
    elif report_type == 'halfyear':
        c.drawString(130, 800, 'Отчет по бронированиям караоке за полгода')

    c.line(50, 780, 550, 780)
    c.line(50, 50, 550, 50)
    y = 740
    k = 1
    index = 1
    for stat in stats:
        if k == 6:
            c.showPage()
            c.setFont("test", 20)
            c.drawString(160, 800, 'Отчет по бронированиям караоке')
            c.line(50, 780, 550, 780)
            c.line(50, 50, 550, 50)
            k = 1
            y = 740
        c.drawString(50, y, str(index))
        c.drawString(100, y, stat.timeslot_id.room.name)
        c.drawString(160, y - 25, 'Дата:')
        c.drawString(160, y - 50, 'Время:')
        c.drawString(160, y - 75, 'Количество бронирований: ')
        c.drawString(160, y - 100, 'Общая выручка : ')
        c.drawString(465, y - 25, str(stat.timeslot_id.date))
        c.drawString(465, y - 50, str(stat.timeslot_id.time))
        c.drawString(465, y - 75, str(stat.total_bookings))
        c.drawString(465, y - 100, str(stat.total_sum) + " руб")
        y -= 140
        k += 1
        index += 1

    c.save()
    c.showPage()
