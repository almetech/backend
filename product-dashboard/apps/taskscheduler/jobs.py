import csv
import io
from datetime import datetime

from decouple import UndefinedValueError, config
from django.core.mail import EmailMessage, get_connection, send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from apps.accounts.models import User
from apps.dashboard.models import (Dailyproductlisting, Productdetails,
                                   Productlisting, Qanda, Reviews)


def heartbeat():
    print(f"Time: {datetime.now()} - Scheduler is working")


def send_email():
    print("Sending regular emails to admin users")

    mail_subject = "Cron Job Mail"
    from_email = config('EMAIL_HOST_USER')
    to_email = ['accornition@gmail.com']

    message = render_to_string('send_email.html')

    email = EmailMessage(mail_subject, message, from_email=from_email, to=to_email)

    for _model in [Dailyproductlisting, Productdetails, Productlisting, Qanda, Reviews]:
        fields = [field.get_attname_column()[1] for field in _model._meta.fields]
        file_name = _model.__name__
        file_name = file_name.replace('"', r'\"')
        csvfile = io.StringIO()
        writer = csv.writer(csvfile)

        # Write the headers first
        headers = fields
        
        writer.writerow(headers)

        queryset = _model.objects.using('scraped').all()
        
        # Now write the data
        for obj in queryset:
            row = [getattr(obj, field) for field in fields]
            writer.writerow(row)
        
        email.attach(f'{file_name}.csv', csvfile.getvalue(), 'text/csv')
    
    if len(to_email) > 0:
        email.send()

    print("Scheduled mails are sent")
