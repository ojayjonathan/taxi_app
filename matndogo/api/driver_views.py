from .forms import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Driver, Trip, CustomerBooking
from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .doc_schema import *
from rest_framework.decorators import api_view


class DriverProfileView(APIView):
    '''
     api endpoint for driver profile
    '''
    schema = UserSchema()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        '''
        > Returns driver profile details

        '''
        driver = get_object_or_404(Driver, user=request.user)
        return Response(DriverSerializer(driver).data)

    def put(self, request):
        '''
        updates driver details

        '''
        form = UserProfileUpdateForm(request.data)
        if form.is_valid():
            user = request.user
            driver = get_object_or_404(Driver, user=user)
            if form.cleaned_data.get("email"):
                user.email = form.cleaned_data["email"]
                user.save()
            if form.cleaned_data.get("phone_number"):
                driver.phone_number = form.cleaned_data['phone_number']
            if form.cleaned_data.get("profile_image"):
                driver.profile_image = form.cleaned_data["profile_image"]
            driver.save()
            return Response(DriverSerializer(driver).data, status=200)
        return Response(form.errors, status=400)


class DriverTrip(APIView):
    '''
     api endpoint for driver trip  
    '''
    schema = DriverTripSchema()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        driver = get_object_or_404(Driver, user=request.user)
        trip = Trip.objects.filter(driver=driver)
        return Response(TripSerializer(trip,many=True).data)

    def post(self, request):
        '''
        return all customers who have booked a seat in a trip
        `trip_id `: trip id
        '''
        trip = get_object_or_404(Trip, id=request.data.get("trip_id"))
        customers = CustomerBooking.objects.filter(trip=trip,status="P")
        return Response(BookingSerializer(customers, many=True).data, status=200)
