import os, sys
from os.path import join, dirname
from twilio.rest import Client
from dotenv import load_dotenv

sys.path.append(join(dirname(__file__), '..'))
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_phone = os.getenv("TWILIO_PHONE")
to_phone = os.getenv("RECIPIENT_PHONE")

client = Client(account_sid, auth_token)

def notify(message):
    return client.messages.create(from_=from_phone, to=to_phone, body=message).sid