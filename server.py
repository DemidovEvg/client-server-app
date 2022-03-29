import select
import sys
from socket import socket, AF_INET, SOCK_STREAM
from common.utils import get_message, send_message
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, ACTION, TIME, \
    USER, ACCOUNT_NAME, PRESENCE, RESPONSE, ERROR, MESSAGE, SENDER, MESSAGE_TEXT
import json
import logging
import logs.server_log_config
from logs.decorators import log
import time

SERVER_LOGGER = logging.getLogger('server')


@log
def process_client_message(message, messages_list, client):
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента: {message}')

    action = message.get(ACTION)
    time = message.get(TIME)
    account_name = message.get(ACCOUNT_NAME)

    if action == PRESENCE and time and account_name == 'Guest':
        send_message(client, {RESPONSE: 200})
        return

    if action == MESSAGE and time and account_name == 'Guest':
        messages_list.append((account_name, message[MESSAGE_TEXT]))
        return

    send_message(client, {RESPONSE: 400, ERROR: 'Bad Request'})
    return


@log
def main():
    listen_address = DEFAULT_IP_ADDRESS
    listen_port = DEFAULT_PORT

    if '-a' in sys.argv:
        listen_address = sys.argv[sys.argv.index('-a') + 1]

    if '-p' in sys.argv:
        listen_port = int(sys.argv[sys.argv.index('-p') + 1])

    CLIENTS = []
    MESSAGES = []
    client, address = None, None
    recv_data_lst, send_data_lst, err_lst = None, None, None

    transport = socket(AF_INET, SOCK_STREAM)
    transport.settimeout(1)
    transport.bind((listen_address, listen_port))
    transport.listen()

    SERVER_LOGGER.info(
        f"Сервер запущен. Подключения принимаются "
        f"{f'с адреса: {listen_address}' if listen_address else 'со всех адресов'}. "
        f"Порт для подключений: {listen_port}"
    )

    while True:
        try:
            client, address = transport.accept()
        except OSError as error:
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соедение с клиентом {address}')
            CLIENTS.append(client)

        try:
            if CLIENTS:
                recv_data_lst, send_data_lst, err_lst = select.select(CLIENTS, CLIENTS, [], 0)
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(get_message(client_with_message),
                                           MESSAGES, client_with_message)
                except:
                    SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                       f'отключился от сервера.')
                    CLIENTS.remove(client_with_message)

        if MESSAGES and send_data_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: MESSAGES[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: MESSAGES[0][1]
            }
            del MESSAGES[0]
            for waiting_client in send_data_lst:
                try:
                    send_message(waiting_client, message)
                except:
                    SERVER_LOGGER.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                    waiting_client.close()
                    CLIENTS.remove(waiting_client)
                    SERVER_LOGGER.error('Принято некорретное сообщение от клиента.')


if __name__ == '__main__':
    main()
