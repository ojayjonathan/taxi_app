from .data import *
from rest_framework.decorators import api_view
import random
from .forms import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .models import (Customer, User, Route, Trip,
                     CustomerBooking, UserAddress, Address, City, Street, PasswordResetToken)
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from threading import Thread
from .validators import phone_number_validator
'''
contains documentation schema
'''
from .doc_schema import *
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from .token_generator import password_reset_token
# create a thread to send email


class EmailThead(Thread):
    def __init__(self, email_to,  message):
        super().__init__()
        self.email_to = email_to
        self.message = message

    def run(self):
        recipient_list = [self.email_to, ]
        send_mail("subject", self.message, settings.EMAIL_HOST_USER, recipient_list,
                  fail_silently=True, html_message=self.message)


class UserLogin(APIView):
    """
    login user
    """
    schema = UserLoginSchema()

    def post(self, request):
        form = UserLoginForm(request.data)
        if form.is_valid():
            user = authenticate(email=form.cleaned_data["email"],
                                password=form.cleaned_data["password"])
            if user:
                token = Token.objects.get(user=user).key
                data = UserSerializer(user).data
                data["token"] = token
                return Response(data, status=200)
            return Response({"errors": ["please provide valid credentials"]},
                            status=400)
        return Response(form.errors, status=400)


class CustomerProfileView(APIView):
    '''
    customer view
    '''
    schema = UserSchema()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        '''
        Returns customer profile
        '''
        customer_profile = get_object_or_404(Customer, user=request.user)
        response = CutomerProfileSerializer(customer_profile).data
        return Response(data=response, status=200)

    def put(self, request):
        form = UserProfileUpdateForm(request.data)
        if form.is_valid():
            user = request.user
            customer_profile = get_object_or_404(Customer, user=user)
            if form.cleaned_data.get("email"):
                user.email = form.cleaned_data["email"]
                user.save()
            if form.cleaned_data.get("phone_number"):
                customer_profile.phone_number = form.cleaned_data['phone_number']
            if form.cleaned_data.get("profile_image"):
                customer_profile.profile_image = form.cleaned_data["profile_image"]
            customer_profile.save()
            return Response(CutomerProfileSerializer(customer_profile).data,
                            status=200)

        return Response(form.errors, status=400)


class RegisterCustomer(APIView):
    '''
    register Customer
    '''
    schema = RegistrationSchema()

    def post(self, request):
        form = UserCreationForm(request.data)
        if form.is_valid():
            phone_number = form.cleaned_data["phone_number"]
            if phone_number_validator(phone_number):
                user = form.save()
                customer = Customer(user=user, phone_number=phone_number)
                customer.save()
                data = UserSerializer(user).data
                token = Token.objects.get(user=user).key
                data["token"] = token
                data["phone_number"] = phone_number
                email_to = form.cleaned_data.get("email")
                password = form.cleaned_data["password"]
                message = f"{email_to} <br> {password}"
                EmailThead(email_to, message).start()
                return Response(data, status=200)
            else:
                form.add_error(
                    "phone_number", "Please provide a valid phone number eg +254734536941")
        return Response(form.errors, status=400)


class RouteView(APIView):
    '''
    Returns all routes which the cars operate
    '''

    def get(self, request):
        query = Route.objects.all()
        return Response(RouteSerializer(query, many=True).data)


class TripView(APIView):
    '''
    Returns all trips which are active and not full
    '''

    def get(self, request):
        query = Trip.objects.filter(status="A", available_seats__gt=0)
        response = TripSerializer(query, many=True).data
        return Response(response)


class CustomerBookingView(APIView):
    '''
    customer car booking view
    '''
    schema = CustomerBookingSchema()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns all customer bookings
        """
        customer = get_object_or_404(Customer, user=request.user)
        bookings = CustomerBooking.objects.filter(customer=customer)
        return Response(BookingSerializer(bookings, many=True).data, status=200)

    def post(self, request):
        '''
         customer to book seats in a trip
         '''
        form = BookingForm(request.data)
        if form.is_valid():
            num_seats = form.cleaned_data["seats_number"]
            trip = get_object_or_404(Trip, id=form.cleaned_data["trip_id"])
            customer = get_object_or_404(
                Customer, user=request.user)
            booking, _ = CustomerBooking.objects.get_or_create(
                customer=customer,
                trip=trip,
            )
            booking.seats = num_seats
            booking.save()
            data = BookingSerializer(booking).data
            return Response(data, status=200)
        return Response(form.errors, status=400)

    def put(self, request):
        '''
        Cancel a  booking
        '''
        book_id = request.data.get("book_id")
        customer_booking = get_object_or_404(CustomerBooking, id=book_id)
        customer_booking.status = "C"
        customer_booking.save()
        return Response(BookingSerializer(customer_booking).data)


class UserAddressView(APIView):
    '''
     user address view
    '''
    schema = AddressSchema()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        '''
        Returns a  list of user addresses
        '''
        address = UserAddress.objects.filter(user=request.user)
        return Response(UserAddressSerializer(address, many=True).data)

    def post(self, request,  *args, **kwargs):
        ''''
        create user address
        '''
        form = AddressUpdateForm(request.data)
        user = request.user
        if form.is_valid():
            city = City.objects.filter(
                name__iexact=form.cleaned_data["city"]).first()
            if not city:
                city = City.objects.create(
                    name=form.cleaned_data["city"])
            street = Street.objects.filter(
                name__iexact=form.cleaned_data["street"]).first()
            if not street:
                street = Street.objects.create(
                    name=form.cleaned_data["street"])
            address, created = Address.objects.get_or_create(street=street, city=city,
                                                             zip_code=form.cleaned_data["zip_code"])
            if created:
                address.save()
                user_address, _ = UserAddress.objects.get_or_create(
                    user=user,
                    address=address
                )
                user_address.save()
            return Response(AddressSerializer(address).data)
        return Response(form.errors, status=400)

    def delete(self, request, *args, **kwargs):
        address = get_object_or_404(Address, id=request.data.get("address_id"))
        address.delete()
        return Response(AddressSerializer(address).data)


class ChangePasswordView(APIView):
    """
    An endpoint for changing password.
    """
    schema = ChangePasswordSchema()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=400)
            # set_password also hashes the password that the user will get
            user.set_password(serializer.data.get("new_password"))
            user.save()
            response = {
                'message': 'Password updated successfully',
            }

            return Response(response, status=200)
        return Response(serializer.errors, status=400)


class ForgotPasswordView(APIView):
    schema = ResetPasswordSchema()

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.filter(
                email=serializer.data.get("email")).first()
            if not user:
                return Response({"email": ["User not found"]}, status=400)
            '''
            short code to be used to change password
            short code will be send to the user wich will be used to reset the password 
            instead of sending long password reset token generated by django PasswordResetGenerator 
            
            '''
            token = password_reset_token.make_token(user)
            uid64 = urlsafe_base64_encode(force_bytes(user.pk))
            obj, _ = PasswordResetToken.objects.get_or_create(user=user)
            obj.short_token = self.gen_token()
            obj.reset_token = token
            obj.save()
            # send short_token to user email
            print(obj.short_token)
            return Response({"message": "please check code to your account to change password", "uid": uid64},
                            status=200)
        return Response(serializer.errors, status=400)

    @staticmethod
    def gen_token():
        token = ""
        for _ in range(6):
            token += "1234567890"[random.randint(0, 9)]
        return int(token)

    def put(self, request):
        serializer = NewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            short_code = request.data.get('short_code')
            uidb64 = request.data.get("uid")
            try:
                uid = int(force_bytes(urlsafe_base64_decode(uidb64)))
                password_token = PasswordResetToken.objects.get(
                    user=uid, short_token=short_code)
            except(TypeError, ValueError, OverflowError, PasswordResetToken.DoesNotExist):
                return Response({"message": "Token not found"}, status=400)

            if password_reset_token.check_token(password_token.user, password_token.reset_token):
                user = get_object_or_404(User, id=uid)
                user.set_password(serializer.data.get("new_password"))
                user.save()
                password_token.delete()
                return Response({"message": "Your password has been changed successfuly "}, status=201)
            else:
                return Response({"message": "Your token has expired please generate another token "}, status=400)
        return Response(serializer.errors, status=400)


@api_view(["GET"])
def customer_suport(request):
    return Response({"phone_numbers": SUPPORT_CONTACT})
