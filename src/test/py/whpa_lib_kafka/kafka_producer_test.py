# *******************************************************************************
# IBM Watson Imaging Common Application Framework 3.0                         *
#                                                                             *
# IBM Confidential                                                            *
#                                                                             *
# OCO Source Materials                                                        *
#                                                                             *
# (C) Copyright IBM Corp. 2019                                                *
#                                                                             *
# The source code for this program is not published or otherwise              *
# divested of its trade secrets, irrespective of what has been                *
# deposited with the U.S. Copyright Office.                                   *
# ******************************************************************************/
import importlib
import os
from unittest import mock
from unittest.mock import MagicMock, patch, Mock
from whpa_lib_kafka import kafka_producer
import asynctest


def get_sample_config_path(file_name):
    package_directory = os.path.dirname(os.path.abspath(__file__))
    root_path = "/../../../../sample_config"
    return os.path.join(package_directory + root_path, file_name)


class TestKafkaProducer(asynctest.TestCase):

    async def setUp(self) -> None:
        os.environ["WHPA_KAFKA_BROKER_CONFIG_FILE"] = get_sample_config_path('kafka.env')
        importlib.reload(kafka_producer.configurations)

    async def test_send_message(self):
        callback_function = None

        def set_callback_function(topic_to_send, msg, key, callback, headers):
            nonlocal callback_function
            callback_function = callback

        def call_callback_success():
            nonlocal callback_function
            callback_function(None, '')

        def call_callback_failiure():
            nonlocal callback_function
            callback_function('error', '')

        producer = kafka_producer.KafkaProducer('mytopic')
        producer.producer = Mock()
        producer.producer.produce = Mock()
        producer.producer.produce.side_effect = set_callback_function
        producer.producer.flush = Mock()
        producer.producer.flush.side_effect = call_callback_success
        result = await producer.send_message('test message')
        producer.producer.produce.assert_called()
        self.assertIsNotNone(result)

        producer.producer.produce.side_effect = set_callback_function
        producer.producer.flush.side_effect = call_callback_failiure
        try:
            result = await producer.send_message('test_message')
            self.fail('Expecteced Exception')
        except Exception as e:
            self.assertTrue(type(e) == Exception)

        try:
            result = await producer.send_message(5)
            self.fail('Expecteced Exception')
        except Exception as e:
            self.assertTrue(type(e) == ValueError)

        producer.producer = None
        try:
            result = await producer.send_message('test_message')
            self.fail('Expecteced Exception')
        except Exception as e:
            self.assertTrue(type(e) == ValueError)


if __name__ == '__main__':
    asynctest.main()
