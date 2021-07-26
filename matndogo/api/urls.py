from django.urls import path
from .views import (CustomerProfileView,customer_suport, RegisterCustomer, ChangePasswordView,Feedback,
                    RouteView, TripView, UserAddressView,  CustomerBookingView, UserLogin, ForgotPasswordView)
from rest_framework.documentation import include_docs_urls
from .driver_views import DriverProfileView, DriverTrip

API_TITLE = 'Car booking api documentation'
API_DESCRIPTION = '...'


urlpatterns = [
    path("address/", UserAddressView.as_view()),
    path("auth/login/", UserLogin.as_view()),
    path("auth/change-password/", ChangePasswordView.as_view()),
    path("auth/customer/register/", RegisterCustomer.as_view()),
    path("auth/reset/", ForgotPasswordView.as_view()),
    path("trip/", TripView.as_view()),
    path("customer/booking/", CustomerBookingView.as_view()),
    path("routes/", RouteView.as_view()),
    path('customer/profile/', CustomerProfileView.as_view()),
    path('driver/profile/', DriverProfileView.as_view()),
    path('driver/trip/', DriverTrip.as_view()),
    path('support/', customer_suport),
    path('docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)),
    path('feedback/', Feedback.as_view()),

]
