import boto3


class AWSClients:
    def user(self):
        client = boto3.client('ssm')
        response = client.get_parameter(Name='user', WithDecryption=True)
        param = response['Parameter']
        val = param['Value']
        return val

    def pass_(self):
        client = boto3.client('ssm')
        response = client.get_parameter(Name='pass', WithDecryption=True)
        param = response['Parameter']
        val = param['Value']
        return val

    def qr_code(self):
        client = boto3.client('ssm')
        response = client.get_parameter(Name='qr', WithDecryption=True)
        param = response['Parameter']
        val = param['Value']
        return val

    def access_key(self):
        client = boto3.client('ssm')
        response = client.get_parameter(Name='ACCESS_KEY', WithDecryption=True)
        param = response['Parameter']
        val = param['Value']
        return val

    def secret_key(self):
        client = boto3.client('ssm')
        response = client.get_parameter(Name='SECRET_KEY', WithDecryption=True)
        param = response['Parameter']
        val = param['Value']
        return val

    def sender(self):
        client = boto3.client('ssm')
        response = client.get_parameter(Name='SENDER', WithDecryption=True)
        param = response['Parameter']
        val = param['Value']
        return val

    def recipient(self):
        client = boto3.client('ssm')
        response = client.get_parameter(Name='RECIPIENT', WithDecryption=True)
        param = response['Parameter']
        val = param['Value']
        return val

    def send(self):
        client = boto3.client('ssm')
        response = client.get_parameter(Name='SEND', WithDecryption=True)
        param = response['Parameter']
        val = param['Value']
        return val

    def receive(self):
        client = boto3.client('ssm')
        response = client.get_parameter(Name='RECEIVE', WithDecryption=True)
        param = response['Parameter']
        val = param['Value']
        return val

    def sid(self):
        client = boto3.client('ssm')
        response = client.get_parameter(Name='SID', WithDecryption=True)
        param = response['Parameter']
        val = param['Value']
        return val

    def token(self):
        client = boto3.client('ssm')
        response = client.get_parameter(Name='TOKEN', WithDecryption=True)
        param = response['Parameter']
        val = param['Value']
        return val
