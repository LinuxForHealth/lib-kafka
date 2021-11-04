"""
kafka_consumer.py

AsyncIO Kafka Consumer
"""
from asyncio import create_task, gather, sleep, get_running_loop
from confluent_kafka import Consumer

from . import config as configurations, logger_util, logging_codes
from .message_segmenter import combine_segments

logger = logger_util.get_logger(__name__)

_DEFAULT_CONCURRENT_LISTENERS = 4
_DEFAULT_MONITOR_FREQUENCY = 60  # This is the monitoring frequency in secs on the number of listener tasks active


class KafkaConsumer:
    """
    AsyncIO Compatible Kafka Consumer which monitors one or more topics.
    Supports pause/unpause listening operations and streaming data via a callback function.
    Callback functions have an expectation of being async.
    """
    def __init__(self, topics, *, concurrent_listeners=None, monitor_frequency=None):
        """
        Configues the KafkaConsumer instance.
        :param topics: iterable of topic names
        :param concurrent_listeners: The number of concurrent consumer listeners. Defaults to _DEFAULT_CONCURRENT_LISTENERS.
        :param monitor_frequency: The number of seconds a listener is monitored. Defaults to _DEFAULT_MONITOR_FREQUENCY.
        """
        broker_config = configurations.KafkaSettings().dict(by_alias=True)
        self.auto_commit_enabled = True
        if 'enable.auto.commit' in broker_config and broker_config['enable.auto.commit'] == False:
            self.auto_commit_enabled = False
        self.consumer = Consumer(broker_config)
        self.topics = topics
        self.concurrent_listeners = concurrent_listeners if concurrent_listeners is not None else _DEFAULT_CONCURRENT_LISTENERS
        self.monitor_frequency = monitor_frequency if monitor_frequency is not None else _DEFAULT_MONITOR_FREQUENCY
        self.tasks = None
        self.done = False
        self.monitor_task = None
        self.paused = False

    def _get_running_loop(self):
        try:
            return get_running_loop()
        except RuntimeError as e:
            logger.error(logging_codes.NO_ACTIVE_LOOP)
            raise e

    async def start_listening(self, callback):
        """
        Starts the Kafka Consumer and registers a callback method.
        The callback method is executed when a message is received.
        The callback signature is `(message: str, headers: Dict)`

        The consume will continue listening until it is paused or closed.

        :param callback: The callback function.
        """
        if self.consumer is None:
            logger.error(logging_codes.CONSUMER_NOT_INITIALIZED)
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
                    logger.warn(logging_codes.LISTENER_EXITED, str(e), exc_info=e)
                    for task in self.tasks:
                        if task.done():
                            self.tasks.remove(task)
                            self.tasks.append(create_task(self._listening_task(callback)))

    def pause(self):
        """Pauses the consumer"""
        self.paused = True

    def unpause(self):
        """Resumes the consumer"""
        self.paused = False

    async def _task_monitor(self, tasks):
        while not self.done:
            if self.paused:
                logger.info(logging_codes.MONITOR_IS_PAUSED)
            else:
                logger.info(logging_codes.MONITOR_LOG, len(self.tasks))
            await sleep(self.monitor_frequency)

    async def _listening_task(self, callback):
        logger.info(logging_codes.STARTING_LISTENER)
        self.consumer.subscribe(self.topics)
        loop = self._get_running_loop()
        while True:
            if self.paused:
                await sleep(5)
                continue
            msgs = await loop.run_in_executor(None, self.consumer.consume, 1)
            for msg in msgs:
                if msg.error():
                    logger.error(logging_codes.CONSUMER_ERROR, msg.error())
                    continue

                headers = msg.headers()
                if headers is None:
                    message = msg.value()
                else:
                    headers = self._generate_header_dictionary(msg.headers())
                    message = combine_segments(msg.value(), headers)

                if not self.auto_commit_enabled:
                    logger.info(logging_codes.COMMITTING_MESSAGE)
                    self.consumer.commit(msg)

                if message is not None:
                    await callback(message, headers)

    def _generate_header_dictionary(self, headers):
        headers_dict = {}
        for key, value in headers:
            headers_dict[key] = value
        return headers_dict

    def close_consumer(self):
        """closes the consumer and cancels any pending tasks"""
        self.done = True
        self.monitor_task.cancel()
        for task in self.tasks:
            task.cancel()
        if self.consumer is not None:
            self.consumer.close()
