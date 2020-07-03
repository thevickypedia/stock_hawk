import time
from datetime import datetime, timedelta, date

import requests

from lib.aws_client import AWSClients

start_time = time.time()
now = datetime.now() - timedelta(hours=5)
dt_string = now.strftime("%A, %B %d, %Y %I:%M %p")


def market_status():
    url = requests.get('https://www.nasdaqtrader.com/trader.aspx?id=Calendar')
    today = date.today().strftime("%B %-d, %Y")
    if today in url.text:
        # doesn't return anything which exits the code
        print(f'{today}: The markets are closed today.')
    else:
        # you can return any random value but it should return something
        return True


def watcher():
    from pyrh import Robinhood
    import json
    import math
    u = AWSClients().user()
    p = AWSClients().pass_()
    q = AWSClients().qr_code()
    rh = Robinhood()
    rh.login(username=u, password=p, qr_code=q)
    print(dt_string)
    print('Gathering your investment details...')
    raw_result = (rh.positions())
    result = raw_result['results']
    shares_total = []
    port_msg = f'Your portfolio:\n'
    loss_output = 'Loss:'
    profit_output = 'Profit:'
    loss_total = []
    profit_total = []
    n = 0
    for data in result:
        share_id = str(data['instrument'].split('/')[-2])
        buy = round(float(data['average_buy_price']), 2)
        shares_count = data['quantity'].split('.')[0]
        if int(shares_count) != 0:
            n = n + 1
        else:
            continue
        raw_details = rh.get_quote(share_id)
        share_name = (raw_details['symbol'])
        call = raw_details['instrument']
        r = requests.get(call)
        response = r.text
        json_load = json.loads(response)
        share_full_name = json_load['simple_name']
        total = round(int(shares_count) * float(buy), 2)
        shares_total.append(total)
        current = (round(float(raw_details['last_trade_price']), 2))
        current_total = round(int(shares_count) * current, 2)
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
    # # use this if you wish to have conditional emails/notifications
    # final_output = f'{output}\n\n{port_msg}\n{profit_output}\n{loss_output}'
    # return final_output
    return port_msg, profit_output, loss_output, output


def send_email():
    port_head, profit, loss, overall_result = watcher()
    from lib.emailer import Emailer
    sender_env = AWSClients().sender()
    recipient_env = AWSClients().recipient()
    logs = 'https://us-west-2.console.aws.amazon.com/cloudwatch/home#logStream:group=/aws/lambda/robinhood'
    git = 'https://github.com/thevickypedia/stock_hawk'
    footer_text = "\n----------------------------------------------------------------" \
                  "----------------------------------------\n" \
                  "A report on the list shares you have purchased.\n" \
                  "The data is being collected using http://api.robinhood.com/," \
                  f"\nFor more information check README.md in {git}"
    sender = f'Robinhood Monitor <{sender_env}>'
    recipient = [f'{recipient_env}']
    title = f'Investment Summary as of {dt_string}'
    text = f'{overall_result}\n\n{port_head}\n{profit}\n{loss}\n\nNavigate to check logs: {logs}\n\n{footer_text}'
    # # use this if you wish to have conditional emails/notifications
    # text = f'{watcher()}\n\nNavigate to check logs: {logs}\n\n{footer_text}'
    Emailer(sender, recipient, title, text)
    return overall_result


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
        client.messages.create(body=f'{dt_string}\nRobinhood Report\n{send_email()}\n\nCheck your email for '
                                    f'summary',
                               from_=from_number,
                               to=to_number)
        print(f"Script execution time: {round(float(time.time() - start_time), 2)} seconds")
    else:
        return  # a plain return acts as a break statement as the None value is not used anywhere


if __name__ == '__main__':
    send_whatsapp("data", "context")
