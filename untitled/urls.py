"""untitled URL Configuration

Бронирование караоке комнат
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static

from untitled import views
from untitled import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.main),
    url(r'^contact/$', views.contact),
    url(r'^sign_in/$', views.login),
    url(r'^register/$', views.register),
    url(r'^guest/$', views.guest),
    url(r'^logout/$', views.logout),
    url(r'^my_karaoke/$', views.mykaraoke),
    url(r'^room_review/(\w+)/$', views.room_review),
    url(r'^price/$', views.price),
    url(r'^room/(\w+)/$', views.room_detail),
    url(r'^upcoming/$', views.upcoming_rooms),
    url(r'^print_booking/$', views.print_booking),
    url(r'^room_video/(\w+)/$', views.room_video),
    url(r'^cabinet/$', views.karaoke_cabinet),
    url(r'^cabinet/page/(\d+)/$', views.karaoke_cabinet),
    url(r'^upcoming/page/(\d+)/$', views.upcoming_rooms),
    url(r'^booking/slot/slot_id=(\d+)/$', views.booking),
    url(r'^booking/quote/$', views.booking_quote),
    url(r'^payment/(\d+)/$', views.payment_page),
    url(r'^payment/(\d+)/pay/$', views.payment_confirm),
    url(r'^payment/(\d+)/success/$', views.payment_success),
    url(r'^payment/webhook/$', views.payment_webhook),
    url(r'^booking/(\d+)/cancel/$', views.cancel_booking),
    url(r'^print_report/(\w+)/$', views.print_report),
    url(r'^(?P<url_date>[\w-]+)/page/(?P<page_number>\d+)/$', views.main),
    url(r'^(?P<url_date>[\w-]+)/$', views.main),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)
