## whi-caf-lib-kafka

Library to create, delete and update kafka topics

## Available API Methods

### create_topic
    This function looks for env variable values of CAF_KAFKA_BROKER_CONFIG_FILE and CAF_KAFKA_TOPIC_CONFIG_FILE for kafka broker and topic configuration file lcoation and created the topic based on that.

### delete_topic(topic_name)

    This function accepts the str parameter topic_name and deletes it if the topic is found in kafka else it logs the error.

### update_partition((topic_name, partition_size, recreate_topic)

    Params:
        topic_name (str): kafka topic name for which partition has to be updated.
        partition_size (int): New total numbers of parititions
        recreate_topic (bool): True in case the topic has to be deleted and recreated for the scenario when requested partition number is less than current partition number.

    This function can be used to increase or decrease the number of current partitions for a topic. For decreasing partition numbers, the topic has to be deleted and recreated. Pass recreate_topic value as True to decrease partition numbers.
