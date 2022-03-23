from common.variables import ENCODING, MAX_PACKAGE_LENGTH
import json
from logs.decorators import log


@log
def get_message(client):
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)

    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)

        if isinstance(response, dict):
            return response

    raise ValueError


@log
def send_message(sock, message):
    if not isinstance(message, dict):
        raise TypeError

    message = json.dumps(message)
    encoded_message = message.encode(ENCODING)
    sock.send(encoded_message)
