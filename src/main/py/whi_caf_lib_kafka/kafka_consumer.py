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

from asyncio import create_task, gather, sleep, get_running_loop
from confluent_kafka import Consumer

import caf_logger.logger as caflogger
from whi_caf_lib_kafka import logging_codes
from whi_caf_lib_kafka.config import broker_config
from whi_caf_lib_kafka.message_segmenter import combine_segments


logger = caflogger.get_logger('whi-caf-lib-kafka')


_DEFAULT_CONCURRENT_LISTENERS = 4
_DEFAULT_MONITOR_FREQUENCY = 3


class KafkaConsumer:
    def __init__(self, topics, *, concurrent_listeners=None, monitor_ferquency=None):
        self.auto_commit_enabled = True
        if 'enable.auto.commit' in broker_config and broker_config['enable.auto.commit'].lower() == 'false':
            self.auto_commit_enabled = False
        self.consumer = Consumer(broker_config)
        self.topics = topics
        self.concurrent_listeners = concurrent_listeners if concurrent_listeners is not None else _DEFAULT_CONCURRENT_LISTENERS
        self.monitor_ferquency = monitor_ferquency if monitor_ferquency is not None else _DEFAULT_MONITOR_FREQUENCY
        self.tasks = None
        self.done = False
        self.monitor_task = None

    def _get_running_loop(self):
        try:
            return get_running_loop()
        except RuntimeError as e:
            logger.error(logging_codes.WHI_CAF_KAFKA_NO_ACTIVE_LOOP)
            raise e

    async def start_listening(self, callback):
        if self.consumer is None:
            logger.error(logging_codes.WHI_CAF_KAFKA_CONSUMER_NOT_INITIALIZED)
            raise ValueError('cannot start listening when consumer is not initialized')
        self.tasks = [create_task(self._listening_task(callback)) for _ in range(self.concurrent_listeners)]
        self.monitor_task = create_task(self._task_monitor(self.tasks))
        while not self.done:
            try:
                await gather(*self.tasks)
            except Exception as e:
                if self.done:
                    for task in self.tasks:
                        if task.done():
                            self.tasks.remove(task)
                else:
                    logger.warn(logging_codes.WHI_CAF_KAFKA_LIB_LISTENER_EXITED, str(e), exc_info=e)
                    for task in self.tasks:
                        if task.done():
                            self.tasks.remove(task)
                            self.tasks.append(create_task(self._listening_task(callback)))

    async def _task_monitor(self, tasks):
        while not self.done:
            logger.info(logging_codes.WHI_CAF_KAFKA_MONITOR_LOG, len(self.tasks))
            await sleep(self.monitor_ferquency)

    async def _listening_task(self, callback):
        logger.info(logging_codes.WHI_CAF_KAFKA_STARTING_LISTENER)
        self.consumer.subscribe(self.topics)
        loop = self._get_running_loop()
        while True:
            msgs = await loop.run_in_executor(None, self.consumer.consume, 1)
            for msg in msgs:
                if msg.error():
                    logger.error(logging_codes.WHI_CAF_KAFKA_CONSUMER_ERROR, msg.error())
                    continue
                
                headers = msg.headers()
                if headers is None:
                    message = msg.value()
                else:
                    message = combine_segments(msg.value(), self._generate_header_dictionary(msg.headers()))

                if not self.auto_commit_enabled:
                    logger.info(logging_codes.WHI_CAF_KAFKA_COMMITTING_MESSAGE)
                    self.consumer.commit(msg)

                if message is not None:
                    await callback(message)

    def _generate_header_dictionary(self, headers):
        headers_dict = {}
        for key, value in headers:
            headers_dict[key] = value
        return headers_dict

    def close_consumer(self):
        self.done = True
        self.monitor_task.cancel()
        for task in self.tasks:
            task.cancel()
        if self.consumer is not None:
            self.consumer.close()
