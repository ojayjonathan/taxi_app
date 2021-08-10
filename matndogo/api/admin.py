from django.contrib import admin
from .models import *


class TripPassagers(admin.TabularInline):
    model = CustomerBooking
    fields = ["customer", "seats", "cost", "status"]


class TripAdmin(admin.ModelAdmin):
    list_display = ["route", "vehicle", "available_seats",
                    "driver", "departure", "arrival", "status"]
    inlines = [TripPassagers]


class RouteAdmin(admin.ModelAdmin):
    list_display = ["origin", "destination", "cost"]


class VehicleAdmin(admin.ModelAdmin):
    list_display = ["vehicle_registration_number", "color", "model", "seats"]


class DriverAdmin(admin.ModelAdmin):
    list_display = ["user", "phone_number", "dl_number"]


class CustomerAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "phone_number"]


class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name",
                    "email", "date_joined", "is_staff"]
    search_fields = ["first_name", "last_name", "email"]


class CustomerBookingAdmin(admin.ModelAdmin):
    list_display = ["customer", "seats", "cost", "status"]


class AddressAdmin(admin.ModelAdmin):
    list_display = ("street", "city", "zip_code")


class UserAddressAdmin(admin.ModelAdmin):
    list_display = ("user", "address")


admin.site.register(Customer, CustomerAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Trip, TripAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(City)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(CustomerBooking, CustomerBookingAdmin)
admin.site.register(Street)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserAddress, UserAddressAdmin)
# admin.site.register(Feedback)
# admin.site.register(PasswordResetToken)
# Register your models here.

