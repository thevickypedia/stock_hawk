#! /usr/bin/env python3
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from lib.aws_client import AWSClients

import boto3

acc_key = AWSClients().access_key()
secret_key = AWSClients().secret_key()


class Emailer:
    def __init__(self, sender: str, recipients: list, title: str, text: str, attachment: list = None):
        boto3_ses_client = boto3.Session(
            aws_access_key_id=acc_key,
            aws_secret_access_key=secret_key
        ).client('ses', region_name='us-west-2')

        response_ = self.send_mail(boto3_ses_client, sender, recipients, title, text, attachment)
        print(response_)

    def create_multipart_message(self, sender: str, recipients: list, title: str, text: str, attachment: list = None) -> MIMEMultipart:
        multipart_content_subtype = 'alternative' if text else 'mixed'
        msg = MIMEMultipart(multipart_content_subtype)
        msg['Subject'] = title
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        if text:
            part = MIMEText(text, 'plain')
            msg.attach(part)
        if attachment:
            import os
            for root, dirs, files in os.walk("tmp"):
                for name in files:
                    path = os.path.join(root, name)
                    with open(path, 'rb') as f:
                        part = MIMEApplication(f.read())
                        part.add_header('Content-Disposition', 'attachment', filename=name)
                        msg.attach(part)
        return msg

    def send_mail(self, boto3, sender: str, recipients: list, title: str, text: str, attachment: list = None) -> dict:
        print("Sending email...")
        msg = self.create_multipart_message(sender, recipients, title, text, attachment)
        ses_client = boto3
        return ses_client.send_raw_email(
            Source=sender,
            Destinations=recipients,
            RawMessage={'Data': msg.as_string()}
        )

# # This was used for testing
# if __name__ == '__main__':
#     s = 'xxx@yyy.com'
#     r = ['yyy@xxx.com']
#     ti = "Test"
#     te = "This is the test text"
#     b = "This is the body of the test email"
#     Emailer(s, r, ti, te, b)
