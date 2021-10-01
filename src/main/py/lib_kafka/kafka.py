import os
import sys
from time import sleep

from confluent_kafka import KafkaError
from confluent_kafka.admin import AdminClient, NewTopic, NewPartitions, KafkaException
from . import logging_codes, logger_util, config as configurations


logger = logger_util.get_logger(__name__)

broker_config = configurations.KafkaSettings().dict(by_alias=True)
client = AdminClient(broker_config)
topics = configurations.KafkaTopics.parse_file(os.getenv('KAFKA_TOPIC_CONFIG_FILE',
                                                         default='/var/app/config/kafka-topic.json'))
create_topic_list = [t for t in topics.dict()['__root__']
                     if t[configurations.TOPIC_OPERATION_KEY] == configurations.OperationEnum.create]
update_topic_list = [t for t in topics.dict()['__root__']
                     if t[configurations.TOPIC_OPERATION_KEY] == configurations.OperationEnum.update]
delete_topic_list = [t for t in topics.dict()['__root__']
                     if t[configurations.TOPIC_OPERATION_KEY] == configurations.OperationEnum.delete]


def create_topics():
    """ Create topics """
    logger.info(logging_codes.TOPIC_START_CREATE)
    new_topics = [NewTopic(topic['name'], num_partitions=int(topic['partitions']),
                           replication_factor=int(topic['replication_factor']))
                  for topic in create_topic_list]

    # A dict of<topic,future> is returned.
    result = client.create_topics(new_topics)

    for topic, future in result.items():
        try:
            future.result()  # The result itself is None
            logger.info(logging_codes.CREATE_TOPIC_SUCCESS, topic)
        except KafkaException as e:
            if e.args[0].code() == KafkaError.TOPIC_ALREADY_EXISTS:
                logger.info(logging_codes.TOPIC_EXISTS, topic)
            elif e.args[0].code() == KafkaError._TIMED_OUT:
                logger.error(logging_codes.CONNECTION_TIMEOUT, broker_config["bootstrap.servers"], topic, e)
                sys.exit(1)
            else:
                logger.error(logging_codes.CREATE_TOPIC_FAIL, topic, e, exc_info=e)
                sys.exit(1)
        except Exception as e:
            logger.error(logging_codes.CREATE_TOPIC_FAIL, topic, e, exc_info=e)
            sys.exit(1)


def delete_topics(topic_name=None):
    """ delete topics """
    logger.info(logging_codes.TOPIC_START_DELETE)
    if topic_name is not None: # delete specific topic
        deleted_topics = [topic_name]
    else:
        deleted_topics = [topic['name']
                          for topic in delete_topic_list] # delete all topics proviced in delete_topics_list
    # Returns a dict of <topic,future>.
    result = client.delete_topics(deleted_topics, operation_timeout=30)

    # Wait for operation to finish.
    for topic, future in result.items():
        try:
            future.result()  # The result itself is None
            logger.info(logging_codes.DELETE_TOPIC_SUCCESS, topic)
        except KafkaException as e:
            if e.args[0].code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                logger.info(logging_codes.TOPIC_NOT_EXISTS, topic)
            elif e.args[0].code() == KafkaError._TIMED_OUT:
                logger.error(logging_codes.CONNECTION_TIMEOUT, broker_config["bootstrap.servers"], topic, e)
                sys.exit(1)
            else:
                logger.error(logging_codes.DELETE_TOPIC_FAIL, topic, e, exc_info=e)
                sys.exit(1)
        except Exception as e:
            logger.error(logging_codes.DELETE_TOPIC_FAIL, topic, e, exc_info=e)
            sys.exit(1)


def update_topics():
    """ Update partitions for a topic """
    logger.info(logging_codes.TOPIC_START_UPDATE)
    partition_list = None
    l_topic = client.list_topics(timeout=15)
    for updated_topic in update_topic_list:
        topic_present = False
        topic_name = updated_topic['name']
        partition_size = updated_topic['partitions']
        recreate_topic = updated_topic['recreate_topic']
        for i in iter(l_topic.topics.values()):
            if i.topic == topic_name:
                topic_present = True
                partition_list = list(i.partitions.values())
                replica_list = partition_list[0].replicas
                break
        # If topic exists, check current partition size
        if topic_present:
            _update_topic(partition_list, partition_size, recreate_topic, replica_list, topic_name)
        else:
            logger.info(logging_codes.TOPIC_NOT_FOUND, topic_name)


def _update_topic(partition_list, partition_size, recreate_topic, replica_list, topic_name):
    current_partition_size = len(partition_list)
    if int(partition_size) > current_partition_size:
        _add_partition(partition_size, topic_name)
    elif int(partition_size) == current_partition_size:
        logger.info(logging_codes.PARTITION_NUM_EQUAL,
                    current_partition_size,
                    partition_size,
                    topic_name)
    else:
        # If recreate_topic is set to True delete the topic and create it with new partition
        logger.info(logging_codes.PARTITION_NUM_LESS,
                    partition_size,
                    current_partition_size,
                    topic_name)
        if recreate_topic:
            _recreate_topic(partition_size, replica_list, topic_name)
        else:
            logger.info(logging_codes.PARTITION_NUM_LESS_AND_NOT_RECREATE)


def _recreate_topic(partition_size, replica_list, topic_name):
    global create_topic_list
    logger.info(logging_codes.PARTITION_NUM_LESS_AND_RECREATE, topic_name, partition_size)
    delete_topics(topic_name)
    sleep(5)  # Necessary delay for the operation to complete on cluster
    create_topic_list = [{'name': topic_name, 'partitions': str(partition_size),
                        'replication_factor': str(len(replica_list))}]
    create_topics()


def _add_partition(partition_size, topic_name):
    new_partition = [NewPartitions(topic_name, int(partition_size))]
    fs = client.create_partitions(new_partition, validate_only=False)
    # Wait for operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logger.info(logging_codes.ADD_PARTITION_SUCCESS, topic, partition_size)
        except Exception as e:
            logger.error(logging_codes.ADD_PARTITION_FAIL, topic, e)


def _convert_to_bool(input_str):
    if input_str is not None and input_str.strip().upper() == 'TRUE':
        return True
    else:
        return False


if __name__ == "__main__":
    if create_topic_list:
        create_topics()

    if update_topic_list:
        update_topics()

    if delete_topic_list:
        delete_topics()
