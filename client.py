import sys
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, TIME, USER, \
    ACCOUNT_NAME, RESPONSE, ERROR, PRESENCE, ACTION, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import send_message, get_message
import time
import json
import logging
import logs.client_log_config
from logs.decorators import log

CLIENT_LOGGER = logging.getLogger('client')


@log
def create_presence(account_name='Guest'):
    presence = {
        ACTION: PRESENCE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return presence


@log
def create_message(sock, account_name='Guest'):
    message = input('Введите сообщение для отправки или \'!!!\' для завершения работы: ')
    if message == '!!!':
        sock.close()
        CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
        sys.exit(0)

    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
    return message_dict


@log
def process_answer(message):
    CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


@log
def message_from_server(message):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя '
              f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        CLIENT_LOGGER.info(f'Получено сообщение от пользователя '
                           f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')


@log
def main():
    server_address = DEFAULT_IP_ADDRESS
    server_port = DEFAULT_PORT
    client_mode = 'send'

    if '-a' in sys.argv:
        server_address = sys.argv[sys.argv.index('-a') + 1]

    if '-p' in sys.argv:
        server_port = int(sys.argv[sys.argv.index('-p') + 1])

    if '-m' in sys.argv:
        client_mode = sys.argv[sys.argv.index('-m') + 1]

    CLIENT_LOGGER.info(f'Запущен клиент с парамертами: '
                       f'адрес сервера: {server_address}, порт: {server_port}')

    transport = socket(AF_INET, SOCK_STREAM)
    transport.connect((server_address, server_port))
    CLIENT_LOGGER.info(f'Установлено соединение с сервером {server_address}:{server_port}')
    message_to_server = create_presence()
    send_message(transport, message_to_server)

    try:
        answer = process_answer(get_message(transport))
        CLIENT_LOGGER.debug(f'Принят ответ от сервера: {answer}')
    except (ValueError, json.JSONDecodeError):
        CLIENT_LOGGER.error('Не удалось декодировать сообщение от сервера')
    else:
        if client_mode == 'send':
            print('Режим работы - отправка сообщений.')
        if client_mode == 'listen':
            print('Режим работы - приём сообщений.')
        while True:
            if client_mode == 'send':
                send_message(transport, create_message(transport))
            if client_mode == 'listen':
                message_from_server(get_message(transport))
    finally:
        transport.close()
        CLIENT_LOGGER.info(f'Соединение закрыто.')
        sys.exit(1)


if __name__ == '__main__':
    main()
