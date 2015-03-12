# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.mime.text import MIMEText

def send_email(recipient, sender, subject, body):
    # Create a text/plain message
    msg = MIMEText(body)

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    # Send the message via our own SMTP server
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()

