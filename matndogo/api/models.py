from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.dispatch import receiver


def upload(instance, filename):
    return f"images/{instance.user.id}/{filename}"


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = UserManager()

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


'''
generate authentication  token after a user has been created and send him/her an email
'''


@receiver(post_save, sender=User)
def create_auth_token(sender=None, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.FileField(null=True, blank=True, upload_to=upload)
    phone_number = models.CharField(max_length=13)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"


class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.FileField(null=True, blank=True, upload_to=upload)
    phone_number = models.CharField(max_length=13)
    gender = models.CharField(max_length=1, choices=(
        ("M", "Male"), ("F", "Female")
    ))
    dl_number = models.CharField(max_length=10, unique=True)
    national_id_number = models.CharField(max_length=8, unique=True)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"


class City(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self) -> str:
        return self.name


class Street(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name


class Route(models.Model):
    origin = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="from+")
    destination = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="to")
    cost = models.IntegerField()

    class Meta:
        unique_together = (("origin", "destination"),)

    def __str__(self) -> str:
        return f"{self.origin} - {self.destination}"


class Vehicle(models.Model):
    color = models.CharField(max_length=50)
    model = models.CharField(max_length=100, help_text="vehicle model type")
    seats = models.IntegerField(
        help_text="available number of seats for passangers")
    vehicle_registration_number = models.CharField(max_length=20, unique=True)

    def __str__(self) -> str:
        return f"{self.vehicle_registration_number} - {self.seats} seats"


class Trip(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True)
    departure = models.DateTimeField(null=True, blank=True)
    arrival = models.DateTimeField(null=True, blank=True)
    available_seats = models.IntegerField()
    status = models.CharField(max_length=1, choices=(
        ("C", "canceled"),  ("F", "fulfiled"), ("A", "active")
    ), default="A")

    def __str__(self) -> str:
        return f"{self.route.origin} - {self.route.destination} trip"


class Address(models.Model):
    zip_code = models.CharField(max_length=20)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    street = models.ForeignKey(Street, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "addresses"

    def __str__(self) -> str:
        return f"{self.zip_code} {self.street} {self.city}, Kenya"


class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name="user_address")

    class Meta:
        unique_together = (("user", "address"),)
        db_table = "user_addresses"

    def __str__(self) -> str:
        return f"{self.user} - {self.address}"


class CustomerBooking(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cost = models.IntegerField(default=0, blank=True)
    seats = models.IntegerField(default=0)
    booked_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=(
        ("C", "canceled"), ("P", "pending"), ("F", "fulfiled")
    ), default="P")
    '''
    __initial_booked_seats keep track if the user has changed the number of booked seats
    '''
    __initial_booked_seats = 0

    class Meta:
        unique_together = (("trip", "customer"))

    def __init__(self, *args, **kwargs) -> None:
        # __initial_booked_seats set number of seats before making update
        super(CustomerBooking, self).__init__(*args, **kwargs)
        if self.seats:
            self.__initial_booked_seats = self.seats

    def __str__(self) -> str:
        return f"{self.trip} - {self.customer.user}"

    def clean(self):
        '''
        ensure user does not book more seats than available in  a trip
        '''
        # self.trip.available_seats+self.__initial_booked_seats gives maximum number of
        # seats a user can book
        total_availale_seats = self.trip.available_seats+self.__initial_booked_seats
        if total_availale_seats < self.seats:
            raise ValidationError(
                f"you can only book a maximum of {total_availale_seats} seats")
        if self.seats < 1 and self.status != "C":
            raise ValidationError("you can book a minimum of 1 seat")

    def save(self, *args, **kwargs):
        # de-allocate seats if user cancels a booking
        # self.trip.available_seats+self.__initial_booked_seats gives maximum number of
        # seats a user can book
        total_availale_seats = self.trip.available_seats+self.__initial_booked_seats
        if self.status == "C":
            self.seats = 0
        else:
            total_availale_seats -= self.seats
        self.trip.available_seats = total_availale_seats
        self.trip.save()
        self.cost = self.seats*self.trip.route.cost
        return super().save(*args, **kwargs)


class DriverEarning(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)


class PasswordResetToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    short_token = models.IntegerField(null=True)
    reset_token = models.CharField(max_length=100)

