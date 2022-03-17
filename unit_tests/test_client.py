import unittest
import os
import sys

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    ERROR, RESPONSE
from client import create_presence, process_answer


class TestClientClass(unittest.TestCase):
    test_time = 1.1
    account_name = 'random_name'
    default_account_name = 'Guest'

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_create_presence_returns_dict(self):
        test = create_presence()
        self.assertIsInstance(test, dict)

    def test_create_presence_without_arg_dict_equal(self):
        presence = {
            ACTION: PRESENCE,
            TIME: self.test_time,
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }

        test = create_presence()
        test[TIME] = self.test_time
        self.assertDictEqual(test, presence)

    def test_create_presence_with_arg_dict_equal(self):
        presense = {
            ACTION: PRESENCE,
            TIME: self.test_time,
            USER: {
                ACCOUNT_NAME: self.account_name
            }
        }

        test = create_presence(self.account_name)
        test[TIME] = self.test_time
        self.assertDictEqual(test, presense)

    def test_process_answer_returns_string(self):
        test = process_answer({RESPONSE: 200})
        self.assertIsInstance(test, str)

    def test_process_answer_raises_value_error(self):
        self.assertRaises(
            ValueError,
            process_answer,
            ({ERROR: 'Bad Request'},)
        )

    def test_process_answer_success_equal(self):
        status_code = 200
        message = {
            RESPONSE: status_code,
        }

        test = process_answer(message)
        self.assertEqual(test, f'{status_code} : OK')

    def test_process_answer_error_equal(self):
        error_msg = 'Bad Request'
        status_code = 400
        message = {
            RESPONSE: status_code,
            ERROR: error_msg
        }

        test = process_answer(message)
        self.assertEqual(test, f'{status_code} : {error_msg}')
