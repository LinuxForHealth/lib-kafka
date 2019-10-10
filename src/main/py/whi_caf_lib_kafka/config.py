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

import configparser
import os

from whi_caf_lib_kafka.logger import logger

broker_config = None
topic_config = None
broker_header = 'kafka Broker'
topic_header = 'kafka topic'
keys = ('nifi_host_api', 'registry_host_api')
default_broker_config = {'bootstrap.servers': 'localhost:9092'}
default_topic_config = {'topics': 'testTopic', 'partitions': '1', 'replication_factors': '1'}


class InvalidConfigException(Exception):
    pass


def load_broker_config(config_file):
    global broker_config
    if not broker_config:
        broker_config = {}
        logger.info("loading config file %s", config_file)
        configfile = configparser.ConfigParser()
        configfile.optionxform = str
        configfile.read(config_file)
        if broker_header not in configfile.sections():
            logger.error("Invalid config. Kafka Broker header not found. Exiting...")
            raise InvalidConfigException("Nifi header not found.")
        temp_config = configfile[broker_header]
        if not validate_config(temp_config):
            raise InvalidConfigException("Missing keys")
        broker_config = {**default_broker_config, **temp_config}


def load_topic_config(config_file):
    global topic_config
    if not topic_config:
        topic_config = {}
        logger.info("loading config file %s", config_file)
        configfile = configparser.ConfigParser()
        configfile.optionxform = str
        configfile.read(config_file)
        if topic_header not in configfile.sections():
            logger.error("Invalid config. Kafka Broker header not found. Exiting...")
            raise InvalidConfigException("Nifi header not found.")
        temp_config = configfile[topic_header]
        if not validate_config(temp_config):
            raise InvalidConfigException("Missing keys")
        topic_config = {**default_topic_config, **temp_config}


def validate_config(config):
    valid = True
    for key in keys:
        if key not in config:
            logger.error("Invalid config. Missing %s parameter", key)
            valid = False
    return valid


broker_config_path = os.getenv('CAF_KAFKA_BROKER_CONFIG_FILE')
topic_config_path = os.getenv('CAF_KAFKA_TOPIC_CONFIG_FILE')
if broker_config_path or topic_config_path is None:
    logger.warning(
        "CAF_KAFKA_BROKER_CONFIG_FILE and CAF_KAFKA_TOPIC_CONFIG_FILE environment variable not defined. Loading "
        "default config...")
    broker_config = default_broker_config
    topic_config = default_topic_config

elif not (os.path.exists(broker_config_path) and os.path.isfile(broker_config_path) and os.path.exists(
        topic_config_path)) or not os.path.isfile(topic_config_path):
    logger.warning('Config file not found. Loading default config...')
    broker_config = default_broker_config
    topic_config = default_topic_config
else:
    load_broker_config(broker_config_path)
    load_topic_config(topic_config_path)
