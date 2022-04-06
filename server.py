import select
import sys
from socket import socket, AF_INET, SOCK_STREAM
from common.utils import get_message, send_message
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, ACTION, TIME, \
    USER, ACCOUNT_NAME, PRESENCE, RESPONSE, ERROR, MESSAGE_TEXT, DESTINATION, \
    EXIT, MESSAGE
import logging
import logs.server_log_config
from logs.decorators import log

SERVER_LOGGER = logging.getLogger('server')


@log
def process_client_message(names: dict,
                           message: dict,
                           messages_list: list,
                           client: socket,
                           clients: list):
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента: {message}')

    action = message.get(ACTION)
    time = message.get(TIME)
    user = message.get(USER)
    account_name = user.get(ACCOUNT_NAME) if user else None
    destination = message.get(DESTINATION)
    message_text = message.get(MESSAGE_TEXT)

    if action == PRESENCE and time and account_name:
        if account_name not in names.keys():
            names[account_name] = client
            send_message(client, {RESPONSE: 200})
        else:
            send_message(client, {RESPONSE: 400, ERROR: 'Имя пользователя уже занято'})
            clients.remove(client)
            client.close()
        return
    elif action == MESSAGE and time and account_name and destination and message_text:
        messages_list.append(message)
        return
    elif action == EXIT and account_name:
        clients.remove(names[account_name])
        names[account_name].close()
        del names[account_name]
        return

    send_message(client, {RESPONSE: 400, ERROR: 'Bad Request'})
    return


@log
def process_message(message, names, listen_socks):
    to_user = message[DESTINATION]
    to_sock = names[to_user]
    if to_user in names and to_sock and to_sock in listen_socks:
        send_message(to_sock, message)
        SERVER_LOGGER.info(f'Отправлено сообщение пользователю {to_user} '
                    f'от пользователя {to_user}.')
    elif to_user in names and to_sock not in listen_socks:
        raise ConnectionError
    else:
        SERVER_LOGGER.error(
            f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
            f'отправка сообщения невозможна.')


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
    NAMES = dict()
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
                    process_client_message(NAMES, get_message(client_with_message),
                                           MESSAGES, client_with_message, CLIENTS)
                except:
                    SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                       f'отключился от сервера.')
                    CLIENTS.remove(client_with_message)

        for message in MESSAGES:
            try:
                process_message(message, NAMES, send_data_lst)
            except Exception:
                SERVER_LOGGER.info(f'Связь с клиентом с именем {message[DESTINATION]} была потеряна')
                CLIENTS.remove(NAMES[message[DESTINATION]])
                del NAMES[message[DESTINATION]]
        MESSAGES.clear()


if __name__ == '__main__':
    main()
