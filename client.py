import sys
import threading
from socket import socket, AF_INET, SOCK_STREAM
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, TIME, USER, \
    ACCOUNT_NAME, RESPONSE, ERROR, PRESENCE, ACTION, MESSAGE_TEXT, EXIT, \
    DESTINATION, MESSAGE
from common.utils import send_message, get_message
import time
import json
import logging
import logs.client_log_config
from logs.decorators import log

CLIENT_LOGGER = logging.getLogger('client')


@log
def create_presence(account_name):
    presence = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name,
        }
    }
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return presence


@log
def create_message(sock, account_name):
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки: ')

    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name,
        },
        MESSAGE_TEXT: message,
        DESTINATION: to_user,
    }
    CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')

    try:
        send_message(sock, message_dict)
        CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
    except Exception as e:
        print(e)
        CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
        sys.exit(1)


@log
def create_exit_message(account_name):
    return {
        ACTION: EXIT,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }


@log
def process_answer(message):
    CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


@log
def message_from_server(sock, account_name):
    while True:
        try:
            message = get_message(sock)

            if ACTION in message and message[ACTION] == MESSAGE \
                    and MESSAGE_TEXT in message and message[DESTINATION] == account_name:
                print(f'Получено сообщение от пользователя '
                      f'{message[USER][ACCOUNT_NAME]}:\n{message[MESSAGE_TEXT]}')
                CLIENT_LOGGER.info(f'Получено сообщение от пользователя '
                                   f'{message[USER][ACCOUNT_NAME]}:\n{message[MESSAGE_TEXT]}')
            else:
                CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
            continue


@log
def user_interactive(sock, username):
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_message(username))
            print('Завершение соединения.')
            CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')


def print_help():
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


@log
def main():
    server_address = DEFAULT_IP_ADDRESS
    server_port = DEFAULT_PORT
    account_name = None

    if '-a' in sys.argv:
        server_address = sys.argv[sys.argv.index('-a') + 1]

    if '-p' in sys.argv:
        server_port = int(sys.argv[sys.argv.index('-p') + 1])

    if '-u' in sys.argv:
        account_name = sys.argv[sys.argv.index('-u') + 1]

    print('Консольный месседжер. Клиентский модуль.')

    if account_name:
        print(f'Ваше имя: {account_name}')
    else:
        account_name = input('Введите ваше имя: ')

    CLIENT_LOGGER.info(f'Запущен клиент с парамертами: '
                       f'адрес сервера: {server_address}, порт: {server_port}')

    transport = socket(AF_INET, SOCK_STREAM)
    transport.connect((server_address, server_port))
    CLIENT_LOGGER.info(f'Установлено соединение с сервером {server_address}:{server_port}')
    message_to_server = create_presence(account_name)
    send_message(transport, message_to_server)

    try:
        answer = process_answer(get_message(transport))
        CLIENT_LOGGER.debug(f'Принят ответ от сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except (ValueError, json.JSONDecodeError):
        CLIENT_LOGGER.error('Не удалось декодировать сообщение от сервера')
    else:
        receiver = threading.Thread(target=message_from_server,
                                    args=(transport, account_name),
                                    daemon=True)
        receiver.start()

        user_interface = threading.Thread(target=user_interactive,
                                          args=(transport, account_name),
                                          daemon=True)
        user_interface.start()

        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
