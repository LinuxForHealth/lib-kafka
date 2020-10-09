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
import uuid

import asynctest


class MessageObject():
    def __init__(self, msg, headers, error=None):
        self.msg_msg = msg
        self.error_msg = error
        self.headers_msg = headers

    def headers(self):
        return self.headers_msg

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
        
        msg = MessageObject(b'test_message', [('fragment.identifier', str(uuid.uuid4).encode('utf-8')), ('fragment.count', b'1'), ('fragment.index',b'1')])
        queue.put(msg)
        await sleep(2)
        self.assertEqual(result, b'test_message')

        consumer.close_consumer()
        queue.put(msg)
        queue.put(msg)
        queue.put(msg)
        queue.put(msg)

    async def test_kafka_listener_multipart_message(self):
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
        consumer = kafka_consumer.KafkaConsumer(['some topic'], concurrent_listeners=1)
        consumer.consumer = Mock()
        consumer.consumer.consume = Mock()
        consumer.consumer.consume.side_effect = wait_on_queue

        get_running_loop().create_task(consumer.start_listening(my_callback))
        
        msg_id = str(uuid.uuid4).encode('utf-8')
        msg1 = MessageObject(b'Hello ', [('fragment.identifier', msg_id), ('fragment.count', b'4'), ('fragment.index',b'1')])
        msg2 = MessageObject(b'World!', [('fragment.identifier', msg_id), ('fragment.count', b'4'), ('fragment.index',b'2')])
        msg3 = MessageObject(b' How a', [('fragment.identifier', msg_id), ('fragment.count', b'4'), ('fragment.index',b'3')])
        msg4 = MessageObject(b're you', [('fragment.identifier', msg_id), ('fragment.count', b'4'), ('fragment.index',b'4')])
        queue.put(msg3)
        queue.put(msg4)
        queue.put(msg2)
        queue.put(msg1)
        await sleep(2)
        self.assertEqual(result, b'Hello World! How are you')

        consumer.close_consumer()
        queue.put(msg1)

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
        
        msg = MessageObject(b'test_message', [('fragment.identifier', str(uuid.uuid4()).encode('utf-8')), ('fragment.count', b'1'), ('fragment.index',b'1')])
        queue.put(msg)
        await sleep(2)
        self.assertEqual(result, b'test_message')
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
        msg = MessageObject(b'test_message', [('fragment.identifier', str(uuid.uuid4).encode('utf-8')), ('fragment.count', b'1'), ('fragment.index',b'1')])
        queue.put(msg)
        queue.put(msg)
        queue.put(msg)
        queue.put(msg)
        queue.put(msg)
        

if __name__ == '__main__':
    asynctest.main()