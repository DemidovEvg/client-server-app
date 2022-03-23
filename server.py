import sys
from socket import socket, AF_INET, SOCK_STREAM
from common.utils import get_message, send_message
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, ACTION, TIME, \
    USER, ACCOUNT_NAME, PRESENCE, RESPONSE, ERROR
import json
import logging
import logs.server_log_config

SERVER_LOGGER = logging.getLogger('server')


def process_client_message(message):
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента: {message}')

    action = message.get(ACTION)
    time = message.get(TIME)
    user = message.get(USER)
    account_name = user.get(ACCOUNT_NAME) if user else None

    if action == PRESENCE and time and user and account_name == 'Guest':
        return {RESPONSE: 200}

    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


def main():
    listen_address = DEFAULT_IP_ADDRESS
    listen_port = DEFAULT_PORT

    if '-a' in sys.argv:
        listen_address = sys.argv[sys.argv.index('-a') + 1]

    if '-p' in sys.argv:
        listen_port = int(sys.argv[sys.argv.index('-p') + 1])

    transport = socket(AF_INET, SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.listen()

    SERVER_LOGGER.info(
        f"Сервер запущен. Подключения принимаются "
        f"{f'с адреса: {listen_address}' if listen_address else 'со всех адресов'}. "
        f"Порт для подключений: {listen_port}"
    )

    while True:
        client, address = transport.accept()
        SERVER_LOGGER.info(f'Установлено соедение с клиентом {address}')

        try:
            message_from_cient = get_message(client)
            SERVER_LOGGER.debug(f'Сообщение от клиента: {message_from_cient}')
            response = process_client_message(message_from_cient)
            SERVER_LOGGER.debug(f'Ответ клиенту: {response}')
            send_message(client, response)
        except (ValueError, json.JSONDecodeError):
            SERVER_LOGGER.error('Принято некорретное сообщение от клиента.')
        finally:
            client.close()
            SERVER_LOGGER.info(f'Соединение закрыто')


if __name__ == '__main__':
    main()
