
from firebase_admin import credentials, messaging
import firebase_admin
import datetime
from django.conf import settings
cred =settings.CREDS
default_app = firebase_admin.initialize_app(cred)



def send_multicast(registration_tokens,title,body):
    message = messaging.MulticastMessage(
        android=messaging.AndroidConfig(
            ttl=datetime.timedelta(seconds=360000),
            priority='high',
            notification=messaging.AndroidNotification(
                title=title,
                body=body,
                icon='stock_ticker_update',
                color='#f45342'
            ),
        ),
        tokens=registration_tokens,
    )
    return messaging.send_multicast(message)



def android_message(token,title,body):
    # [START android_message]
    message = messaging.Message(
        android=messaging.AndroidConfig(
            ttl=datetime.timedelta(seconds=360000),
            priority='high',
            notification=messaging.AndroidNotification(
                title=title,
                body=body,
                icon='stock_ticker_update',
                color='#f45342'
            ),
        ),
      token = token
    )
    messaging.send(message)
    return message



