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

from asyncio import get_running_loop, gather
from confluent_kafka import Producer

import caf_logger.logger as caflogger
from whi_caf_lib_kafka import logging_codes
from whi_caf_lib_kafka.message_segmenter import segment_message, ID, COUNT, INDEX
from whi_caf_lib_kafka.config import broker_config


logger = caflogger.get_logger('whi-caf-lib-kafka')

_DEFAULT_SEGMENT_SIZE = 900*1024


class KafkaProducer:
    def __init__(self, topic, segment_size=None):
        self.producer = Producer(broker_config)
        self.topic = topic
        self.segment_size = segment_size if segment_size is not None else _DEFAULT_SEGMENT_SIZE

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
                loop.call_soon_threadsafe(asyncio_callback.set_exception, Exception(err))
            else:
                logger.info(logging_codes.WHI_CAF_KAFKA_MESSAGE_DELIVERED)
                loop.call_soon_threadsafe(asyncio_callback.set_result, msg)
        return set_asyncio_result

    async def send_message(self, msg, *, topic=None, key=None, headers=None):
        if self.producer is None:
            logger.error(logging_codes.WHI_CAF_KAFKA_PRODUCER_NOT_INITIALIZED)
            raise ValueError('cannot send message when producer is not initialized')
        if not type(msg) in [str, bytes]:
            logger.error(logging_codes.WHI_CAF_KAFKA_INVALID_MSG_TYPE)
            raise ValueError('msg can only be of type bytes or string')
        if headers is None:
            headers = {}
        topic_to_send = topic if topic is not None else self.topic
        loop = self._get_running_loop()
        futures = []
        for segment, identifier, count, index in segment_message(msg, self.segment_size):
            segment_headers = {
                ID: identifier,
                COUNT: count,
                INDEX: index
            }
            future = loop.create_future()
            final_headers = {**headers, **segment_headers}
            self.producer.produce(topic_to_send, segment, key=key, callback=self._kafka_callback(loop, future), headers=final_headers)
            futures.append(future)

        logger.info(logging_codes.WHI_CAF_KAFKA_MESSAGE_QUEUED)
        await loop.run_in_executor(None, self.producer.flush)
        await gather(*futures)

        return True
