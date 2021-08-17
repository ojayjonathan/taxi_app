from rest_framework import serializers
from .models import (Customer, Driver, CustomerBooking, Street,
                     Route, User, Trip, City, Address, UserAddress,Vehicle)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "email", "last_name"]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["name"]


class StreetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Street
        fields = ["name"]


class AddressSerializer(serializers.ModelSerializer):
    city = CitySerializer()
    street = StreetSerializer()

    class Meta:
        model = Address
        fields = "__all__"


class UserAddressSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = UserAddress
        fields = ["address", ]


class RouteSerializer(serializers.ModelSerializer):
    origin = CitySerializer()
    destination = CitySerializer()

    class Meta:
        model = Route
        fields = ["origin", "destination", "cost","available"]


class DriverSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Driver
        fields = ["id", "user", "profile_image",
                  "phone_number", "dl_number", "national_id_number", "gender"]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for password reset endpoint.
    """
    email = serializers.EmailField(required=True)


class NewPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    new_password = serializers.CharField()
    short_code = serializers.IntegerField()

class VehicleSerializer(serializers.ModelSerializer):
     class Meta:
        model = Vehicle
        fields = ["vehicle_registration_number","color","seats"]


class TripSerializer(serializers.ModelSerializer):
    route = RouteSerializer()
    driver = DriverSerializer()
    vehicle = VehicleSerializer()
    class Meta:
        model = Trip
        fields = ["id", "route", "arrival",
                  "departure", "status", "available_seats","driver","vehicle"]


class CutomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = ["user", "profile_image", "phone_number"]


class BookingSerializer(serializers.ModelSerializer):
    trip = TripSerializer()
    customer = CutomerProfileSerializer()

    class Meta:
        model = CustomerBooking
        fields = "__all__"