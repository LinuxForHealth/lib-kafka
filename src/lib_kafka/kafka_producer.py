"""
kafka_producer.py

AsyncIO Kafka Producer
"""
from asyncio import get_running_loop, gather
from confluent_kafka import Producer

from . import config as configurations, logger_util, logging_codes
from .message_segmenter import segment_message, ID, COUNT, INDEX


logger = logger_util.get_logger(__name__)

_DEFAULT_SEGMENT_SIZE = 900 * 1024

class KafkaProducer:
    """
    AsyncIO Compatible Kafka Producer, used to send a message to a topic.
    """
    def __init__(self, topic, segment_size=None):
        """
        Configures the Kafka Producer.
        :param topic: Identifies the producer's messaging destination.
        :param segment_size: Used to divide a message in multiple segments prior to transmission.
        """
        broker_config = configurations.KafkaSettings().dict(by_alias=True)
        self.producer = Producer(broker_config)
        self.topic = topic
        self.segment_size = segment_size if segment_size is not None else _DEFAULT_SEGMENT_SIZE

    def _get_running_loop(self):
        try:
            return get_running_loop()
        except RuntimeError as e:
            logger.error(logging_codes.NO_ACTIVE_LOOP)
            raise e

    def _kafka_callback(self, loop, asyncio_callback):
        def set_asyncio_result(err, msg):
            if err is not None:
                logger.warn(logging_codes.MESSAGE_DELIVERY_FAILED, err)
                loop.call_soon_threadsafe(asyncio_callback.set_exception, Exception(err))
            else:
                logger.info(logging_codes.MESSAGE_DELIVERED)
                loop.call_soon_threadsafe(asyncio_callback.set_result, msg)

        return set_asyncio_result

    async def send_message(self, msg, *, topic=None, key=None, headers=None):
        """
        Sends a message to a topic.
        :param msg: The message to send.
        :param topic: Used to override the Producer's default topic, if provided. Defaults to None.
        :param key: The key used to determine which partition the message is sent to. Defaults to None.
        :poram headers: Attaches custom metadata in the form of key/value(dict) to the message. Defaults to None.

        :returns: True when processing completes
        """
        if self.producer is None:
            logger.error(logging_codes.PRODUCER_NOT_INITIALIZED)
            raise ValueError('cannot send message when producer is not initialized')
        if not type(msg) in [str, bytes]:
            logger.error(logging_codes.INVALID_MSG_TYPE)
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
            self.producer.produce(topic_to_send, segment, key=key, callback=self._kafka_callback(loop, future),
                                  headers=final_headers)
            futures.append(future)

        logger.info(logging_codes.MESSAGE_QUEUED)
        await loop.run_in_executor(None, self.producer.flush)
        await gather(*futures)

        return True
