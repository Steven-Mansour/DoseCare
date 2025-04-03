from twilio.rest import Client
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_ACCOUNT_AUTH_TOKEN")
sourcePhoneNb = os.getenv("TWILIO_ACCOUNT_NUMBER")
client = Client(account_sid, auth_token)

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 25))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")


def sendMessage(body, destination):
    # Sending an SMS
    client.messages.create(
        body=body,
        from_=sourcePhoneNb,  # Your Twilio phone number
        to=destination  # Recipient's phone number
    )  # Sending an SMS
    print("Message sent")
    return


def send_email(subject, body, recipients):
    """
    Sends an email synchronously to multiple recipients.

    :param subject: Subject of the email.
    :param body: Email body content.
    :param recipients: List of recipient email addresses.
    """
    try:
        # Create email message
        msg = MIMEMultipart()
        msg["From"] = EMAIL_FROM
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect to SMTP server
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()  # Secure the connection

        # Login to the email account
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)

        # Send email
        server.sendmail(EMAIL_FROM, recipients, msg.as_string())

        # Close the connection
        server.quit()

        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")
