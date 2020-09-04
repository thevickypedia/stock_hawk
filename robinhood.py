import json
import math
import os
import random
import string
import time
from datetime import datetime, timedelta, date

import boto3
import requests
from pyrh import Robinhood

from lib.aws_client import AWSClients

start_time = time.time()
now = datetime.now() - timedelta(hours=5)
dt_string = now.strftime("%A, %B %d, %Y %I:%M %p")

u = AWSClients().user()
p = AWSClients().pass_()
q = AWSClients().qr_code()
rh = Robinhood()
rh.login(username=u, password=p, qr_code=q)
raw_result = rh.positions()
result = raw_result['results']


def market_status():
    url = requests.get('https://www.nasdaqtrader.com/trader.aspx?id=Calendar')
    today = date.today().strftime("%B %d, %Y")
    if today in url.text:
        # doesn't return anything which exits the code
        print(f'{today}: The markets are closed today.')
    else:
        # you can return any random value but it should return something
        return True


def watcher():
    print(dt_string)
    print('Gathering your investment details...')
    shares_total = []
    port_msg = f'Your portfolio:\n'
    loss_output = 'Loss:'
    profit_output = 'Profit:'
    loss_total = []
    profit_total = []
    n = 0
    n_ = 0
    for data in result:
        share_id = str(data['instrument'].split('/')[-2])
        buy = round(float(data['average_buy_price']), 2)
        shares_count = int(data['quantity'].split('.')[0])
        if shares_count != 0:
            n = n + 1
            n_ = n_ + shares_count
        else:
            continue
        raw_details = rh.get_quote(share_id)
        share_name = (raw_details['symbol'])
        call = raw_details['instrument']
        r = requests.get(call)
        response = r.text
        json_load = json.loads(response)
        share_full_name = json_load['simple_name']
        total = round(shares_count * float(buy), 2)
        shares_total.append(total)
        current = (round(float(raw_details['last_trade_price']), 2))
        current_total = round(shares_count * current, 2)
        difference = round(float(current_total - total), 2)
        if difference < 0:
            loss_output += (
                f'\n{share_full_name}:\n{shares_count} shares of {share_name} at ${buy} Currently: ${current}\n'
                f'Total bought: ${total} Current Total: ${current_total}'
                f'\nLOST ${-difference}\n')
            loss_total.append(-difference)
        else:
            profit_output += (
                f'\n{share_full_name}:\n{shares_count} shares of {share_name} at ${buy} Currently: ${current}\n'
                f'Total bought: ${total} Current Total: ${current_total}'
                f'\nGained ${difference}\n')
            profit_total.append(difference)

    lost = round(math.fsum(loss_total), 2)
    gained = round(math.fsum(profit_total), 2)
    port_msg += f'The below values will differ from overall profit/loss if shares were purchased ' \
                f'with different price values.\nTotal Profit: ${gained}\nTotal Loss: ${lost}\n'
    net_worth = round(float(rh.equity()), 2)
    output = f'Total number of stocks purchased: {n}\n'
    output += f'Total number of shares owned: {n_}\n'
    output += f'\nCurrent value of your total investment is: ${net_worth}'
    total_buy = round(math.fsum(shares_total), 2)
    output += f'\nValue of your total investment while purchase is: ${total_buy}'
    total_diff = round(float(net_worth - total_buy), 2)
    if total_diff < 0:
        output += f'\nOverall Loss: ${total_diff}'
    else:
        output += f'\nOverall Profit: ${total_diff}'
    yesterday_close = round(float(rh.equity_previous_close()), 2)
    two_day_diff = round(float(net_worth - yesterday_close), 2)
    output += f"\n\nYesterday's closing value: ${yesterday_close}"
    if two_day_diff < 0:
        output += f"\nCurrent Dip: ${two_day_diff}"
    else:
        output += f"\nCurrent Spike: ${two_day_diff}"
    return port_msg, profit_output, loss_output, output


def watchlists():
    watchlist = (rh.get_watchlists())
    r1, r2 = '', ''
    instruments = []
    for data in result:
        instruments.append(data['instrument'])
    for item in watchlist:
        instrument = item['url']
        if instrument not in instruments:
            stock = item['symbol']
            raw_details = rh.get_quote(stock)
            call = raw_details['instrument']
            historic_data = rh.get_historical_quotes(stock, 'hour', 'day')
            # historic_data = rh.get_historical_quotes(stock, '10minute', 'day')
            historic_results = historic_data['results']
            numbers = []
            for each_item in historic_results:
                historical_values = each_item['historicals']
                for close_price in historical_values:
                    numbers.append(round(float(close_price['close_price']), 2))
            r = requests.get(call)
            response = r.text
            json_load = json.loads(response)
            stock_name = json_load['simple_name']
            price = round(float(raw_details['last_trade_price']), 2)
            difference = round(float(price - numbers[-1]), 2)
            if price < numbers[-1]:
                r1 += f'{stock_name}({stock}) - {price} &#8595 {difference}\n'
            else:
                r2 += f'{stock_name}({stock}) - {price} &#8593 {difference}\n'
    return r1, r2


def send_email():
    port_head, profit, loss, overall_result = watcher()
    from lib.emailer import Emailer
    sender_env = AWSClients().sender()
    recipient_env = AWSClients().recipient()
    logs = 'https://us-west-2.console.aws.amazon.com/cloudwatch/home#logStream:group=/aws/lambda/robinhood'
    git = 'https://github.com/thevickypedia/stock_hawk'
    footer_text = f"Navigate to check logs: {logs}\n\n" \
                  "\n----------------------------------------------------------------" \
                  "----------------------------------------\n" \
                  "A report on the list shares you have purchased.\n" \
                  "The data is being collected using http://api.robinhood.com/," \
                  f"\nFor more information check README.md in {git}"
    sender = f'Robinhood Monitor <{sender_env}>'
    recipient = [f'{recipient_env}']
    title = f'Investment Summary as of {dt_string}'
    text = f'{overall_result}\n\n{port_head}\n' \
           '\n---------------------------------------------------- PROFIT ------------' \
           '----------------------------------------\n' \
           f'\n\n{profit}\n' \
           '\n---------------------------------------------------- LOSS ------------' \
           '----------------------------------------\n' \
           f'\n\n{loss}\n\n{footer_text}'
    # # use this if you wish to have conditional emails/notifications
    # text = f'{watcher()}\n\nNavigate to check logs: {logs}\n\n{footer_text}'
    Emailer(sender, recipient, title, text)


def stasher():
    port_head, profit, loss, overall_result = watcher()
    s1, s2 = watchlists()
    logs = 'https://us-west-2.console.aws.amazon.com/cloudwatch/home#logStream:group=/aws/lambda/robinhood'
    title = f'Investment Summary as of {dt_string}'

    # Stasher to save the file in my public website's secure link instead
    bucket_name = 'thevickypedia.com'
    public_key = AWSClients().public_key()
    private_key = AWSClients().private_key()

    # # Delete existing file
    # s3 = boto3.resource('s3')
    # objects_to_delete = s3.meta.client.list_objects(Bucket=bucket_name, Prefix="/tmp/")
    # delete_keys = {'Objects': [{'Key': k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents', [])]]}
    # s3.meta.client.delete_objects(Bucket=bucket_name, Delete=delete_keys)
    # print(f"{delete_keys['Objects'][0]['Key']} was removed")

    # # Write new file
    # client = boto3.client('s3')
    # required_str = string.ascii_letters
    # public_key = "".join(random.choices(required_str, k=16))
    # secure_str = string.ascii_letters + string.digits
    # private_key = "".join(random.choices(secure_str, k=240))
    # client.put_bucket_website(
    #     Bucket=bucket_name,
    #     WebsiteConfiguration={
    #         'ErrorDocument': {
    #             'Key': 'loader'
    #         },
    #         'IndexDocument': {
    #             'Suffix': 'index'
    #         },
    #         'RoutingRules': [
    #             {
    #                 'Condition': {
    #                     'KeyPrefixEquals': f'{public_key}'
    #                 },
    #                 'Redirect': {
    #                     'ReplaceKeyPrefixWith': f'/tmp/{private_key}'
    #                 }
    #             },
    #             {
    #                 'Condition': {
    #                     'KeyPrefixEquals': 'index.html'
    #                 },
    #                 'Redirect': {
    #                     'ReplaceKeyPrefixWith': 'index'
    #                 }
    #             },
    #             {
    #                 'Condition': {
    #                     'KeyPrefixEquals': 'about.html'
    #                 },
    #                 'Redirect': {
    #                     'ReplaceKeyPrefixWith': 'about'
    #                 }
    #             },
    #             {
    #                 'Condition': {
    #                     'KeyPrefixEquals': 'projects.html'
    #                 },
    #                 'Redirect': {
    #                     'ReplaceKeyPrefixWith': 'projects'
    #                 }
    #             },
    #             {
    #                 'Condition': {
    #                     'KeyPrefixEquals': 'others.html'
    #                 },
    #                 'Redirect': {
    #                     'ReplaceKeyPrefixWith': 'others'
    #                 }
    #             },
    #             {
    #                 'Condition': {
    #                     'KeyPrefixEquals': 'contact.html'
    #                 },
    #                 'Redirect': {
    #                     'ReplaceKeyPrefixWith': 'contact'
    #                 }
    #             },
    #             {
    #                 'Condition': {
    #                     'KeyPrefixEquals': 'insights.html'
    #                 },
    #                 'Redirect': {
    #                     'ReplaceKeyPrefixWith': 'insights'
    #                 }
    #             },
    #             {
    #                 'Condition': {
    #                     'KeyPrefixEquals': 'loader.html'
    #                 },
    #                 'Redirect': {
    #                     'ReplaceKeyPrefixWith': 'loader'
    #                 }
    #             },
    #         ]
    #     }
    # )
    web_text = f'\n\n{overall_result}\n\n{port_head}\n'
    # profit_text = '\n---------------------------------------------------- PROFIT ------------' \
    #               '----------------------------------------\n'
    profit_web = f'\n\n{profit}\n'
    # loss_text = '\n---------------------------------------------------- LOSS ------------' \
    #             '----------------------------------------\n'
    loss_web = f'\n{loss}\n\n'

    upload_file = f'/tmp/{private_key}'
    name_file = os.path.isfile(upload_file)
    if name_file:
        os.remove(upload_file)
    file = open(upload_file, 'w')
    data = f"""<!DOCTYPE html>
            <html>
            <head>
            <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
            <meta http-equiv="Pragma" content="no-cache">
            <meta http-equiv="Expires" content="0">
            <link href="https://{bucket_name}/css/stock_hawk.css" rel="stylesheet" Type="text/css">
            </head>
            <body><p class="center">{title}</p>
            <p class="tab"><span style="white-space: pre-line">{web_text}</span></p>
            <div class="dotted"></div>
            <div class="cent">Profit</div>
            <div class="dotted"></div>
            <p class="tab"><span style="white-space: pre-line">{profit_web}</span></p>
            <div class="dotted"></div>
            <div class="cent">Loss</div>
            <div class="dotted"></div>
            <p class="tab"><span style="white-space: pre-line">{loss_web}</span></p>
            <div class="dotted"></div>
            <div class="cent">Watchlist</div>
            <div class="dotted"></div>
            <p class="tab"><span style="white-space: pre-line">{s2}</span></p>
            <p class="tab"><span style="white-space: pre-line">{s1}</span></p>
            <div class="footer"><div align="center" class="content">
            <p>Navigate to check <a href="{logs}" target="_bottom">logs</a></p>
            </div></div><br><br></body></html>"""
    file.write(data)
    file.close()
    mimetype = 'text/html'
    object_name = upload_file
    s3_client = boto3.client('s3')
    s3_client.upload_file(upload_file, bucket_name, object_name, ExtraArgs={"ContentType": mimetype})
    print(f'Stored {public_key} in the S3 bucket: {bucket_name}')

    return f"{overall_result}\n\nCheck the url https://{bucket_name}/{public_key}"


# two arguments for the below functions as lambda passes event, context by default
def send_whatsapp(data, context):
    if market_status():
        from twilio.rest import Client
        whatsapp_send = AWSClients().send()
        whatsapp_receive = AWSClients().receive()
        sid = AWSClients().sid()
        token = AWSClients().token()
        client = Client(sid, token)
        from_number = f"whatsapp:{whatsapp_send}"
        to_number = f"whatsapp:{whatsapp_receive}"
        client.messages.create(body=f'{dt_string}\nRobinhood Report\n{stasher()}',
                               from_=from_number,
                               to=to_number)
        print(f"Script execution time: {round(float(time.time() - start_time), 2)} seconds")


if __name__ == '__main__':
    send_whatsapp("data", "context")
