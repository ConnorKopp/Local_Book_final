from django.contrib import admin

from .models import AvailableDate, Booking, Venue

admin.site.register(Venue)
admin.site.register(AvailableDate)
admin.site.register(Booking)