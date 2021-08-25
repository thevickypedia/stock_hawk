from boto3 import client


class AWSClients:
    def __init__(self):
        self.client = client('ssm')

    def robinhood_user(self):
        response = self.client.get_parameter(Name='/Jarvis/robinhood_user', WithDecryption=True)
        return response['Parameter']['Value']

    def robinhood_pass(self):
        response = self.client.get_parameter(Name='/Jarvis/robinhood_pass', WithDecryption=True)
        return response['Parameter']['Value']

    def robinhood_qr(self):
        response = self.client.get_parameter(Name='/Jarvis/robinhood_qr', WithDecryption=True)
        return response['Parameter']['Value']

    def gmail_user(self):
        response = self.client.get_parameter(Name='/Jarvis/gmail_user_secondary', WithDecryption=True)
        return response['Parameter']['Value']

    def gmail_pass(self):
        response = self.client.get_parameter(Name='/Jarvis/gmail_pass_secondary', WithDecryption=True)
        return response['Parameter']['Value']

    def phone_number(self):
        response = self.client.get_parameter(Name='/Jarvis/phone_number', WithDecryption=True)
        return response['Parameter']['Value']

    def private_key(self):
        response = self.client.get_parameter(Name='private_key', WithDecryption=True)
        return response['Parameter']['Value']

    def public_key(self):
        response = self.client.get_parameter(Name='public_key', WithDecryption=True)
        return response['Parameter']['Value']
