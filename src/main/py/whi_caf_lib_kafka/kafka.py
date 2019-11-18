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
from time import sleep
from confluent_kafka.admin import AdminClient, NewTopic, NewPartitions
from whi_caf_lib_kafka import logging_codes
from whi_caf_lib_kafka.config import broker_config, create_topic_list, update_topic_list, delete_topic_list
import caf_logger.logger as caflogger
import os

logger = caflogger.get_logger('whi-caf-lib-kafka')

client = AdminClient(broker_config)
new_topics_list = create_topic_list
deleted_topics_list = delete_topic_list


def create_topics():
    """ Create topics """

    new_topics = [NewTopic(topic['name'], num_partitions=int(topic['partitions']),
                           replication_factor=int(topic['replication_factor']))
                  for topic in new_topics_list]

    # Call create_topics to asynchronously create topics, a dict
    # of <topic,future> is returned.
    fs = client.create_topics(new_topics)

    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logger.info(logging_codes.WHI_CAF_KAFKA_LIB_CREATE_TOPIC_SUCCESS, topic)
        except Exception as e:
            logger.error(logging_codes.WHI_CAF_KAFKA_LIB_CREATE_TOPIC_FAIL, topic, e, exc_info=e)


def delete_topics():
    """ delete topics """
    deleted_topics = [topic['name']
                      for topic in deleted_topics_list]
    # Returns a dict of <topic,future>.
    fs = client.delete_topics(deleted_topics, operation_timeout=30)

    # Wait for operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logger.info(logging_codes.WHI_CAF_KAFKA_LIB_DELETE_TOPIC_SUCCESS, topic)
        except Exception as e:
            logger.error(logging_codes.WHI_CAF_KAFKA_LIB_DELETE_TOPIC_FAIL, topic, e, exc_info=e)


def update_topics(recreate_topic=False):
    """ Update partitions for a topic """
    global new_topics_list, deleted_topics_list
    partition_list = None
    l_topic = client.list_topics(timeout=15)
    for updated_topic in update_topic_list:
        topic_present = False
        topic_name = updated_topic['name']
        partition_size = updated_topic['partitions']
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
            logger.info(logging_codes.WHI_CAF_LIB_TOPIC_NOT_FOUND, topic_name)


def _update_topic(partition_list, partition_size, recreate_topic, replica_list, topic_name):
    current_partition_size = len(partition_list)
    if int(partition_size) > current_partition_size:
        _add_partition(partition_size, topic_name)
    elif int(partition_size) == current_partition_size:
        logger.info(logging_codes.WHI_CAF_KAFKA_LIB_PARTITION_NUM_EQUAL,
                    current_partition_size,
                    partition_size,
                    topic_name)
    else:
        # If recreate_topic is set to True delete the topic and create it with new partition
        logger.info(logging_codes.WHI_CAF_KAFKA_LIB_PARTITION_NUM_LESS,
                    partition_size,
                    current_partition_size,
                    topic_name)
        if recreate_topic:
            _recreate_topic(partition_size, replica_list, topic_name)
        else:
            logger.info(logging_codes.WHI_CAF_KAFKA_LIB_PARTITION_NUM_LESS_AND_NOT_RECREATE)


def _recreate_topic(partition_size, replica_list, topic_name):
    global deleted_topics_list, new_topics_list
    logger.info(logging_codes.WHI_CAF_KAFKA_LIB_PARTITION_NUM_LESS_AND_RECREATE, topic_name)
    deleted_topics_list = [{'name': topic_name}]
    delete_topics()
    sleep(5)  # Necessary delay for the operation to complete on cluster
    new_topics_list = [{'name': topic_name, 'partitions': str(partition_size),
                        'replication_factor': str(len(replica_list))}]
    create_topics()


def _add_partition(partition_size, topic_name):
    new_partition = [NewPartitions(topic_name, int(partition_size))]
    fs = client.create_partitions(new_partition, validate_only=False)
    # Wait for operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logger.info(logging_codes.WHI_CAF_KAFKA_LIB_ADD_PARTITION_SUCCESS, topic)
        except Exception as e:
            logger.error(logging_codes.WHI_CAF_KAFKA_LIB_ADD_PARTITION_FAIL, topic, e)


def _convert_to_bool(input_str):
    if input_str is not None and input_str.strip().upper() == 'TRUE':
        return True
    else:
        return False


if __name__ == "__main__":
    kafka_operation = os.getenv('CAF_KAFKA_TOPIC_OPERATION')
    if 'CREATE' == kafka_operation:
        create_topics()
    elif 'UPDATE' == kafka_operation:
        update_topics(_convert_to_bool(os.getenv('RECREATE_TOPIC')))
    elif 'DELETE' == kafka_operation:
        delete_topics()
