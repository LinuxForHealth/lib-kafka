## lib-kafka

Library to create, delete and update kafka topics

The required environment variables before making following API calls:

KAFKA_BROKER_CONFIG_FILE: The config file path for broker configuration. Default value is "/var/app/config/kafka.env"

Sample kafka.env content:

    bootstrap_servers = localhost:9093
    group_id = kafka-listener
    security_protocol = PLAINTEXT
    ssl_ca_location = /var/app/certs/kafka/tls.crt
    enable_auto_commit = False

KAFKA_TOPIC_CONFIG_FILE: The config file path for topic configuration. Default value is "/var/app/config/kafka-topic.json"

Sample kafka-topics.json content:

    [
        {
            "name": "test_topic_1",
            "replication_factor": 1,
            "partitions": 1,
            "operation": "CREATE"
        },
        {
            "name": "test_topic_1",
            "replication_factor": 1,
            "partitions": 1,
            "recreate_topic": true,
            "operation": "UPDATE"
        },
        {
            "name": "test_topic_2",
            "operation": "DELETE"
        }
    ]
