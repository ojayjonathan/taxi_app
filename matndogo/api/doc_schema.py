from rest_framework.schemas import AutoSchema
import coreapi


class RegistrationSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if method.lower() == 'post':
            extra_fields = [
                coreapi.Field("email", required=True, location="form"),
                coreapi.Field("first_name", required=True, location="form"),
                coreapi.Field("last_name", required=True, location="form"),
                coreapi.Field("phone_number", required=True, location="form",
                              description="must start with +254... eg +254742116141"),
                coreapi.Field("password", required=True, location="form"),
            ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


class UserLoginSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        fields = [coreapi.Field("email", required=True, location="form"),
                  coreapi.Field("password", required=True, location="form"), ]
        manual_fields = super().get_manual_fields(path, method)
        return fields + manual_fields


class UserSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if method.lower() == 'put':
            extra_fields = [
                coreapi.Field("email", required=False, location="form"),
                coreapi.Field("phone_number", required=False, location="form"),
                coreapi.Field("profile_image", required=False,
                              location="form", schema=None),

            ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


class CustomerBookingSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if method.lower() == 'post':
            extra_fields = [
                coreapi.Field("trip_id", required=True, location="form"),
                coreapi.Field("seats_number", required=True, location="form"),

            ]
        if method.lower() == "put":
            extra_fields = [
                coreapi.Field("book_id", required=True, location="form",
                              description="id of booking to cancel"),


            ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


class AddressSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if method.lower() == 'post':
            extra_fields = [
                coreapi.Field("street", required=True, location="form"),
                coreapi.Field("zip_code", required=True, location="form"),
                coreapi.Field("city", required=True, location="form")

            ]
        if method.lower() == "delete":
            extra_fields = [
                coreapi.Field("address_id", required=True, location="form",
                              description="id of booking to cancel"),
            ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


class ChangePasswordSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = [
            coreapi.Field("new_password", required=True, location="form"),
            coreapi.Field("old_password", required=True, location="form")

        ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


class PasswordSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = [
            coreapi.Field("email", required=True, location="form"),
        ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


class ResetPasswordSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if method.lower() == "post":
            extra_fields = [
                coreapi.Field("email", required=True, location="form"),
            ]
        if method.lower() == "put":
            extra_fields = [
                coreapi.Field("uid", required=True, location="form"),
                coreapi.Field("short_code", required=True, location="form"),
                coreapi.Field("new_password", required=True, location="form"),
            ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields


class DriverTripSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if method.lower() == "post":
            extra_fields = [
                coreapi.Field("trip_id", required=True, location="form"),
            ]
        # if method.lower() == "put":
        #     extra_fields = [
        #         coreapi.Field("uid", required=True, location="form"),
        #         coreapi.Field("short_code", required=True, location="form"),
        #         coreapi.Field("new_password", required=True, location="form"),
        #     ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields
