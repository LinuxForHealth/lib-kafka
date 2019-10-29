## whi-caf-lib-kafka

Library to create, delete and update kafka topics

The required environment variables before making following API calls:

CAF_KAFKA_BROKER_CONFIG_FILE: The config file path for broker configuration. Default value is "/var/app/config/caf-kafka.cfg"

Sample caf-kafka.cfg content:

    bootstrap.servers=localhost:9093
    security.protocol=SSL
    ssl.ca.location=/var/app/certs/kafka/tls.crt

CAF_KAFKA_TOPIC_CONFIG_FILE: The config file path for topic configuration. Default value is "/var/app/config/caf-kafka-topics.cfg"

Sample caf-kafka-topics.cfg content:

    [kafka topic operation]
    create_topics = queue1,queue2 
    delete_topics = queue2,queue3
    update_topics = queue1,queue4


    [queue1]
    name = queue1
    partitions = 2
    replication_factor = 1

    [queue2]
    name = queue2
    partitions = 2
    replication_factor = 1

    [queue3]
    name = queue3
    partitions = 2
    replication_factor = 1

    [queue4]
    name = queue4
    partitions = 2
    replication_factor = 1

In the above sample file, as shown, the "kafka topic operation" section should have the values of queue names for corresponding operation type as a comma separated values. There should be a section for each queue name that is defined in "kafka topic operation" section

CAF_KAFKA_TOPIC_OPERATION: Valid values are CREATE, UPDATE and DELETE. Default value is CREATE.

## Available API Methods

### create_topics()
    This function is used to create topics as per configuration in the kafka topic config file defined by env var CAF_KAFKA_TOPIC_CONFIG_FILE

### delete_topics(topic_name)

    This function is used to delete topics as per configuration in the kafka topic config file defined by env var CAF_KAFKA_TOPIC_CONFIG_FILE

### update_topics(recreate_topic=False)

    Params:
        recreate_topic (bool): True in case the topic has to be deleted and recreated for the scenario when requested partition number is less than current partition number. The default value is False

    This function can be used to increase or decrease the number of current partitions for topics as per configuration in the kafka topic config file defined by env var CAF_KAFKA_TOPIC_CONFIG_FILE. For decreasing partition numbers, the topic has to be deleted and recreated. Pass recreate_topic value as True to decrease partition numbers.
