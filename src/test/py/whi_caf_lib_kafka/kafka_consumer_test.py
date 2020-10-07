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

from unittest import mock
from unittest.mock import MagicMock, patch, Mock
from queue import Queue
from whi_caf_lib_kafka import kafka_consumer
from asyncio import get_running_loop, sleep, all_tasks
import time

import asynctest


class MessageObject():
    def __init__(self, msg, error=None):
        self.msg_msg = msg
        self.error_msg = error

    def error(self):
        return self.error_msg

    def value(self):
        return self.msg_msg

class TestKafkaProducer(asynctest.TestCase):

    async def test_kafka_listener(self):
        queue = Queue()
        def wait_on_queue(*args):
            msg = queue.get()
            return [msg]

        result = None
        async def my_callback(msg):
            nonlocal result
            result = msg

        broker_config = {
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'kafka-listener',
            'enable.auto.commit': 'True'
        }
        kafka_consumer.broker_config = broker_config
        consumer = kafka_consumer.KafkaConsumer(['some topic'])
        consumer.consumer = Mock()
        consumer.consumer.consume = Mock()
        consumer.consumer.consume.side_effect = wait_on_queue

        get_running_loop().create_task(consumer.start_listening(my_callback))
        
        msg = MessageObject('test_message')
        queue.put(msg)
        await sleep(2)
        self.assertEqual(result.value(), 'test_message')

        consumer.close_consumer()
        queue.put(msg)
        queue.put(msg)
        queue.put(msg)
        queue.put(msg)

    async def test_kafka_listener_auto_commit_disabled(self):
        queue = Queue()
        def wait_on_queue(*args):
            msg = queue.get()
            return [msg]

        result = None
        async def my_callback(msg):
            nonlocal result
            result = msg

        broker_config = {
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'kafka-listener',
            'enable.auto.commit': 'False'
        }
        kafka_consumer.broker_config = broker_config
        consumer = kafka_consumer.KafkaConsumer(['some topic'], concurrent_listeners=1)
        consumer.consumer = Mock()
        consumer.consumer.consume = Mock()
        consumer.consumer.commit = Mock()
        consumer.consumer.consume.side_effect = wait_on_queue

        get_running_loop().create_task(consumer.start_listening(my_callback))
        
        msg = MessageObject('test_message')
        queue.put(msg)
        await sleep(2)
        self.assertEqual(result.value(), 'test_message')
        consumer.consumer.commit.assert_called()
        consumer.close_consumer()
        queue.put(msg)
        

    async def test_kafa_listner_with_none_consumer(self):
        broker_config = {
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'kafka-listener',
            'enable.auto.commit': 'False'
        }
        kafka_consumer.broker_config = broker_config
        consumer = kafka_consumer.KafkaConsumer(['some topic'])
        consumer.consumer = None
        try:
            await consumer.start_listening(None)
            self.fail('expected exception. non thrown')
        except ValueError:
            pass
        except BaseException as e:
            self.fail('unexpected exception ' + str(e))

    async def test_kafka_listener_restart_listener(self):
        queue = Queue()
        def wait_on_queue(*args):
            msg = queue.get()
            return [msg]

        result = None
        async def my_callback(msg):
            nonlocal result
            result = msg

        broker_config = {
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'kafka-listener',
            'enable.auto.commit': 'False'
        }
        kafka_consumer.broker_config = broker_config
        consumer = kafka_consumer.KafkaConsumer(['some topic'])
        consumer.consumer = Mock()
        consumer.consumer.consume = Mock()
        consumer.consumer.consume.side_effect = wait_on_queue

        get_running_loop().create_task(consumer.start_listening(my_callback))
        
        await sleep(2)
        self.assertEqual(len(consumer.tasks), 4)
        consumer.tasks[0].cancel()
        await sleep(2)
        self.assertEqual(len(consumer.tasks), 4)
        
        consumer.close_consumer()
        msg = MessageObject('test_message')
        queue.put(msg)
        queue.put(msg)
        queue.put(msg)
        queue.put(msg)
        queue.put(msg)
        

if __name__ == '__main__':
    asynctest.main()
