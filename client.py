import sys
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT
from common.utils import send_message, get_message
import time
import json


def create_presence(account_name='Guest'):
    presence = {
        'action': 'presence',
        'time': time.time(),
        'user': {
            'account_name': account_name
        }
    }
    return presence


def process_answer(message):
    if 'response' in message:
        if message['response'] == 200:
            return '200 : OK'
        return f'400 : {message["error"]}'
    raise ValueError


if __name__ == '__main__':
    server_address = DEFAULT_IP_ADDRESS
    server_port = DEFAULT_PORT

    if '-a' in sys.argv:
        server_address = sys.argv[sys.argv.index('-a') + 1]

    if '-p' in sys.argv:
        server_port = int(sys.argv[sys.argv.index('-p') + 1])

    transport = socket(AF_INET, SOCK_STREAM)
    transport.connect((server_address, server_port))
    message_to_server = create_presence()
    send_message(transport, message_to_server)

    try:
        answer = process_answer(get_message(transport))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение сервера.')

    transport.close()
