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
from confluent_kafka.admin import AdminClient, NewTopic, NewPartitions
import sys
from whi_caf_lib_kafka.logger import logger

conf = dict(line.strip().split('=') for line in open('/var/app/config/caf-kafka.cfg') if
            not line.startswith('#') and not line.startswith('\n'))
client = AdminClient(conf)

topic_config = dict(line.strip().split('=') for line in open('/var/app/config/caf-kafka-topics.cfg') if
                    not (line.startswith('#') or line.startswith('\n')))

topics = topic_config["topics"].split(",")
partitions = topic_config["partitions"].split(",")
replication_factors = topic_config["replication_factors"].split(",")


def create_topics():
    """ Create topics """

    new_topics = [NewTopic(topics[i], num_partitions=int(partitions[i]), replication_factor=int(replication_factors[i]))
                  for i in range(len(topics))]
    # Call create_topics to asynchronously create topics, a dict
    # of <topic,future> is returned.
    fs = client.create_topics(new_topics)

    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logger.info("Topic {} created".format(topic))
        except Exception as e:
            logger.error("Failed to create topic {}: {}".format(topic, e))


def delete_topics():
    """ delete topics """

    # Returns a dict of <topic,future>.
    fs = client.delete_topics(topics, operation_timeout=30)

    # Wait for operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logger.info("Topic {} deleted".format(topic))
        except Exception as e:
            logger.error("Failed to delete topic {}: {}".format(topic, e))


def add_partitions():
    """ Add partitions """

    new_parts = [NewPartitions(topics[i], int(partitions[i])) for
                 i in range(len(topics))]

    fs = client.create_partitions(new_parts, validate_only=False)

    # Wait for operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logger.info("Additional partitions created for topic {}".format(topic))
        except Exception as e:
            logger.error("Failed to add partitions to topic {}: {}".format(topic, e))


if __name__ == '__main__':

    operation = sys.argv[1]
    # Create Admin client
    # client = AdminClient({'bootstrap.servers': broker})

    opsmap = {'create_topics': create_topics,
              'delete_topics': delete_topics,
              'add_partitions': add_partitions}

    if operation not in opsmap:
        sys.stderr.write('Unknown operation: %s\n' % operation)
        sys.exit(1)

    opsmap[operation]()
