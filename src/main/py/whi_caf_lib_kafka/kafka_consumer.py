# *******************************************************************************
# IBM Watson Imaging Common Application Framework 3.1                           *
#                                                                               *
# IBM Confidential                                                              *
#                                                                               *
# OCO Source Materials                                                          *
#                                                                               *
# Copyright IBM Corporation 2019, 2020                                          *
#                                                                               *
# The source code for this program is not published or otherwise                *
# divested of its trade secrets, irrespective of what has been                  *
# deposited with the U.S. Copyright Office.                                     *
# *******************************************************************************

from asyncio import create_task, gather, get_event_loop, sleep
from confluent_kafka import Consumer
import time
import random

import caf_logger.logger as caflogger
from whi_caf_lib_kafka import logging_codes
from whi_caf_lib_kafka.config import broker_config


logger = caflogger.get_logger('whi-caf-lib-kafka')


_DEFAULT_CONCURRENT_LISTENERS = 4
_DEFAULT_MONITOR_FREQUENCY = 30

class KafkaConsumer:
    def __init__(self, topics, *, concurrent_listeners=None, monitor_ferquency=None):
        self.auto_commit_enabled = False
        if 'enable.auto.commit' not in broker_config or broker_config['enable.auto.commit'].lower != 'false':
            self.auto_commit_enabled = True
        self.consumer = Consumer(broker_config)
        self.topics = topics
        self.concurrent_listeners = concurrent_listeners if concurrent_listeners is not None else _DEFAULT_CONCURRENT_LISTENERS
        self.monitor_ferquency = monitor_ferquency if monitor_ferquency is not None else _DEFAULT_MONITOR_FREQUENCY
        self.tasks = None

    async def start_listening(self, callback):
        if self.consumer is None:
            logger.error(logging_codes.WHI_CAF_KAFKA_CONSUMER_NOT_INITIALIZED)
            raise ValueError('cannot start listening when consumer is not initialized')
        self.tasks = [create_task(self._listening_task(callback)) for i in range(self.concurrent_listeners)]
        create_task(self._task_monitor(self.tasks))
        while True:
            try:
                await gather(*self.tasks)
            except Exception as e:
                logger.warn(logging_codes.WHI_CAF_KAFKA_LIB_LISTENER_EXITED, str(e), exc_info=e)
                for task in self.tasks:
                    if task.done():
                        self.tasks.remove(task)
                        self.tasks.append(create_task(self._listening_task(callback)))

    async def _task_monitor(self, tasks):
        while True:
            logger.info(logging_codes.WHI_CAF_KAFKA_MONITOR_LOG, len(self.tasks))
            await sleep(self.monitor_ferquency)

    async def _listening_task(self, callback):
        logger.info(logging_codes.WHI_CAF_KAFKA_STARTING_LISTENER)
        self.consumer.subscribe(self.topics)
        while True:
            msgs = await loop.run_in_executor(None, self.consumer.consume, 1)
            for msg in msgs:
                if msg is None:
                    pass
                elif msg.error():
                    logger.error(logging_codes.WHI_CAF_KAFKA_CONSUMER_ERROR, msg.error())

                await callback(msg)

                if not self.auto_commit_enabled:
                    logger.info(logging_codes.WHI_CAF_KAFKA_COMMITTING_MESSAGE)
                    self.consumer.commit(msg)

    def close_consumer(self):
        if self.consumer is not None:
            self.consumer.close()


### DELETE this later
async def message_handler(msg):
    print('Received message in handler: {}'.format(msg.value().decode('utf-8')))

if __name__ == '__main__':
    loop = get_event_loop()
    kafka_consumer = KafkaConsumer(['mytopic'])
    loop.run_until_complete(kafka_consumer.start_listening(message_handler))
