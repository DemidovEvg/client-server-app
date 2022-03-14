import sys
from socket import socket, AF_INET, SOCK_STREAM
from common.utils import get_message, send_message
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT
import json


def process_client_message(message):
    action = message.get('action')
    time = message.get('time')
    user = message.get('user')
    account_name = user.get('account_name') if user else None

    if action == 'presence' and time and user and account_name == 'Guest':
        return {'response': 200}

    return {
        'response': 400,
        'error': 'Bad Request'
    }


if __name__ == '__main__':
    listen_address = DEFAULT_IP_ADDRESS
    listen_port = DEFAULT_PORT

    if '-a' in sys.argv:
        listen_address = sys.argv[sys.argv.index('-a') + 1]

    if '-p' in sys.argv:
        listen_port = int(sys.argv[sys.argv.index('-p') + 1])

    transport = socket(AF_INET, SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.listen()

    while True:
        client, address = transport.accept()

        try:
            message_from_cient = get_message(client)
            print(message_from_cient)
            response = process_client_message(message_from_cient)
            send_message(client, response)
        except (ValueError, json.JSONDecodeError):
            print('Принято некорретное сообщение от клиента.')

        client.close()
