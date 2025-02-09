from twilio.rest import Client
import os
from dotenv import load_dotenv
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_ACCOUNT_AUTH_TOKEN")
sourcePhoneNb = os.getenv("TWILIO_ACCOUNT_NUMBER")
client = Client(account_sid, auth_token)


def sendMessage(body, destination):
    # Sending an SMS
    client.messages.create(
        body=body,
        from_=sourcePhoneNb,  # Your Twilio phone number
        to=destination  # Recipient's phone number
    )  # Sending an SMS
    print("Message sent")
    return
