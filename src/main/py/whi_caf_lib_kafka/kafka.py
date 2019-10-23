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
from whi_caf_lib_kafka.config import topic_config, broker_config
import caf_logger.logger as caflogger

logger = caflogger.get_logger('whi-caf-lib-kafka')

client = AdminClient(broker_config)
topics = topic_config["topics"].split(",")
partitions = topic_config["partitions"].split(",")
replication_factors = topic_config["replication_factors"].split(",")


def create_topic():
    """ Create topic """

    new_topics = [NewTopic(topics[i], num_partitions=int(partitions[i]), replication_factor=int(replication_factors[i]))
                  for i in range(len(topics))]
    # Call create_topic to asynchronously create topics, a dict
    # of <topic,future> is returned.
    fs = client.create_topics(new_topics)

    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logger.info(logging_codes.WHI_CAF_KAFKA_LIB_CREATE_TOPIC_SUCCESS, topic)
        except Exception as e:
            logger.error(logging_codes.WHI_CAF_KAFKA_LIB_CREATE_TOPIC_FAIL, topic, e, exc_info=e)


def delete_topic(topic_name):
    """ delete topic """
    global topics
    topics = topic_name.split(",")
    # Returns a dict of <topic,future>.
    fs = client.delete_topics(topics, operation_timeout=30)

    # Wait for operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logger.info(logging_codes.WHI_CAF_KAFKA_LIB_DELETE_TOPIC_SUCCESS, topic)
        except Exception as e:
            logger.error(logging_codes.WHI_CAF_KAFKA_LIB_DELETE_TOPIC_FAIL, topic, e, exc_info=e)


def update_partition(topic_name, partition_size, recreate_topic=False):
    """ Update partitions for a topic """
    global topics
    global partitions
    global replication_factors
    topic_present = False
    partition_list = None
    l_topic = client.list_topics(timeout=15)
    for i in iter(l_topic.topics.values()):
        if i.topic == topic_name:
            topic_present = True
            partition_list = list(i.partitions.values())
            replica_list = partition_list[0].replicas
            break
    # If topic exists, check current partition size
    if topic_present:
        current_partition_size = len(partition_list)
        if int(partition_size) > current_partition_size:
            new_partition = [NewPartitions(topic_name, int(partition_size))]
            fs = client.create_partitions(new_partition, validate_only=False)
            # Wait for operation to finish.
            for topic, f in fs.items():
                try:
                    f.result()  # The result itself is None
                    logger.info(logging_codes.WHI_CAF_KAFKA_LIB_ADD_PARTITION_SUCCESS, topic)
                except Exception as e:
                    logger.error(logging_codes.WHI_CAF_KAFKA_LIB_ADD_PARTITION_FAIL, topic, e)
        elif int(partition_size) == current_partition_size:
            logger.info(logging_codes.WHI_CAF_KAFKA_LIB_PARTITION_NUM_EQUAL, current_partition_size, partition_size)
        else:
            # If recreate_topic is set to True delete the topic and create it with new partition
            logger.info(logging_codes.WHI_CAF_KAFKA_LIB_PARTITION_NUM_LESS, partition_size, current_partition_size)
            if recreate_topic:
                logger.info(logging_codes.WHI_CAF_KAFKA_LIB_PARTITION_NUM_LESS_AND_RECREATE, topic_name)
                topics = [topic_name]
                delete_topic(topic_name)
                sleep(2)
                partitions = [str(partition_size)]
                replication_factors = [str(len(replica_list))]
                create_topic()
            else:
                logger.info(logging_codes.WHI_CAF_KAFKA_LIB_PARTITION_NUM_LESS_AND_NOT_RECREATE)
    else:
        logger.info(logging_codes.WHI_CAF_LIB_TOPIC_NOT_FOUND, topic_name)
