
from django.core.validators import MinValueValidator
from threading import Thread
from django.conf import settings
from django.core.mail import send_mail
from .app_notifications import send_multicast
from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


def upload(instance, filename):
    return f"images/{instance.user.id}/{filename}"


class EmailThead(Thread):
    def __init__(self, email_to,  message):
        super().__init__()
        self.email_to = email_to
        self.message = message

    def run(self):
        send_mail("subject",  self.message, settings.EMAIL_HOST_USER, self.email_to,
                  fail_silently=True, html_message=self.message)


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
    profile_image = models.ImageField(null=True, blank=True, upload_to=upload)
    phone_number = models.CharField(max_length=13)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"


class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(null=True, blank=True, upload_to=upload)
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
        City, on_delete=models.CASCADE, related_name="travel_origin")
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
    available_seats = models.IntegerField(validators=[MinValueValidator(0)])
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
        ("C", "canceled"), ("A", "active"), ("F", "fulfiled")
    ), default="A")
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

# send notification when the trip is full


@receiver(post_save, sender=CustomerBooking)
def send_user_notification(sender=None, instance=None, created=False, **kwargs):
    if created:
        message = f'''{instance.customer.user} has booked a trip from 
                         {instance.trip.route.origin} to {instance.trip.route.destination}'''
        EmailThead(["matndogo254@gmail.com"], message)
        
    try:
        if instance.status == "A" and instance.trip.available_seats == 0:
            trip_users = CustomerBooking.objects.filter(
                trip=instance.trip, status="A")
            tokens = [token.fcm_token for token in Fcm.objects.filter(
                user__in=[item.customer.user.id for item in trip_users])]
            # push notification
            message = "The trip you booked is full, you will receive a confirmation call."
            EmailThead([item.customer.email for item in trip_users] +
                       ["matndogo254@gmail.com"], message)
            send_multicast(tokens, "Booking status update",
                           message)
            # email notication

    except:
        pass


class DriverEarning(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)


class PasswordResetToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    short_token = models.IntegerField(null=True)
    reset_token = models.CharField(max_length=100)


class Feedback(models.Model):
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_on = models.DateTimeField(auto_created=True, default=timezone.now)


class Fcm(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    fcm_token = models.CharField(max_length=200)
