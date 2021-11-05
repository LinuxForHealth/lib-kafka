# LinuxForHealth lib-kafka

The [asyncio](https://docs.python.org/3/library/asyncio.html) LinuxForHealth [Kafka](https://kafka.apache.org/) client. lib-kafka provides asyncio based
implementations of the Kakfa Consumer, Producer, and Admin APIs.

## Quickstart

### Pre-requisites

* Python >= 3.8
* librdkafka >= 1.6.0

LinuxForHealth lib-kafka is built on Confluent's Kafka Python client, which in turn relies on a "native" C dependency, librdkafka.
librdkafka is included in Confluent's Kafka-Python wheel distribution for some platforms. For other platforms it needs to be installed prior to use.
Please refer to [Confluent's documentation](https://github.com/confluentinc/confluent-kafka-python#prerequisites) for additional information.

### Project Setup and Validation
```shell
git clone https://github.com/LinuxForHealth/lib-kafka
cd lib-kafka

python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip setuptools 
pip install -e .[test]
pytest
```

## Configuration

lib-kafka uses environment variables to specify configuration file locations. Supported environment variables include: 

* KAFKA_BROKER_CONFIG_FILE
* KAFKA_TOPIC_CONFIG_FILE

### KAFKA_BROKER_CONFIG_FILE
The path to the Kafka broker configuration file. Default value is "/var/app/config/kafka.env"

Sample kafka.env content:

    bootstrap_servers = localhost:9093
    group_id = kafka-listener
    security_protocol = PLAINTEXT
    ssl_ca_location = /var/app/certs/kafka/tls.crt
    enable_auto_commit = False

### KAFKA_TOPIC_CONFIG_FILE
The path to the Kafka topic configuration. Default value is "/var/app/config/kafka-topic.json"
The topic configuration file manages topics using create, delete, and update operations.

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

## Usage

### Kafka Consumer
The Kafka Consumer streams events from one or more topics. The code below initializes and starts a Kafka Consumer.
The script requires both the `KAFKA_BROKER_CONFIG_FILE` and `KAFKA_TOPIC_CONFIG_FILE` to be set in the environment.  

```python
import asyncio
from lib_kafka.kafka_consumer import KafkaConsumer
from typing import Dict

TOPIC_NAME = "test_topic"

async def consumer_callback(msg: str, headers: Dict):
    """"
    Executes when the consumer receives a message from the subscribed topic.
    Note that the method is defined as async and is expected to "await" on I/O
    
    :param msg: The streamed message
    :param headers: The message headers 
    """
    asyncio.sleep(1) # arbitrary asyncio wait for demonstration
    print(msg)
    print(headers)

loop = asyncio.get_event_loop()
consumer = KafkaConsumer([TOPIC_NAME])
# start_listening is awaitable
loop.create_task(consumer.start_listening(consumer_callback))
loop.run_forever()
```

### Kafka Producer
The Kafka Producer sends a message to a topic. The code below initializes a KafkaProducer and sends a message. 
The script requires both the `KAFKA_BROKER_CONFIG_FILE` and `KAFKA_TOPIC_CONFIG_FILE` to be set in the environment.  

```python
import asyncio
from lib_kafka.kafka_producer import KafkaProducer

TOPIC_NAME = "test_topic"

loop = asyncio.get_event_loop()
producer = KafkaProducer(TOPIC_NAME)
# send_message is awaitable
loop.create_task(producer.send_message("test message"))
loop.run_forever()
```
