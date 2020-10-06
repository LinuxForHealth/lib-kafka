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

from asyncio import create_task, gather, get_event_loop, sleep, get_running_loop
from confluent_kafka import Producer
import time
import random

import caf_logger.logger as caflogger
from whi_caf_lib_kafka import logging_codes
from whi_caf_lib_kafka.config import broker_config


logger = caflogger.get_logger('whi-caf-lib-kafka')


class KafkaProducer:
    def __init__(self, topic):
        self.producer = Producer(broker_config)
        self.topic = topic

    def _get_running_loop(self):
        try:
            return get_running_loop()
        except RuntimeError as e:
            logger.error(logging_codes.WHI_CAF_KAFKA_NO_ACTIVE_LOOP)
            raise e

    def _kafka_callback(self, loop, asyncio_callback):
        def set_asyncio_result(err, msg):
            if err is not None:
                logger.warn(logging_codes.WHI_CAF_KAFKA_LIB_MESSAGE_DELIVERY_FAILED, err)
                loop.call_soon_threadsafe(asyncio_callback.set_exception, err)
            else:
                logger.info(logging_codes.WHI_CAF_KAFKA_MESSAGE_DELIVERED)
                loop.call_soon_threadsafe(asyncio_callback.set_result, msg)
        return set_asyncio_result

    async def send_message(self, msg, *, topic=None, key=None, headers=None):
        if self.producer is None:
            logger.error(logging_codes.WHI_CAF_KAFKA_PRODUCER_NOT_INITIALIZED)
            raise ValueError('cannot send message when producer is not initialized')
        topic_to_send = topic if topic is not None else self.topic
        loop = self._get_running_loop()
        future = loop.create_future()
        self.producer.produce(topic_to_send, msg, key=key, callback=self._kafka_callback(loop, future), headers=headers)
        await loop.run_in_executor(None, self.producer.flush)
        logger.info(logging_codes.WHI_CAF_KAFKA_MESSAGE_QUEUED)
        await future

        return future.result(), future.exception()

    def close_producer(self):
        if self.producer is not None:
            self.producer.close()
