# *******************************************************************************
# IBM Watson Imaging Common Application Framework 3.1                           *
#                                                                               *
# IBM Confidential                                                              *
#                                                                               *
# OCO Source Materials                                                          *
#                                                                               *
# Copyright IBM Corporation 2019, 2020                                          *
#                                                                               *
# The source code for this program is not published or otherwise                *
# divested of its trade secrets, irrespective of what has been                  *
# deposited with the U.S. Copyright Office.                                     *
# *******************************************************************************

import os

import caf_logger.logger as caflogger
from whi_caf_lib_configreader import config as configreader
from whi_caf_lib_kafka import logging_codes

logger = caflogger.get_logger('whi-caf-lib-kafka')

broker_config = None
create_topic_list = []
delete_topic_list = []
update_topic_list = []
_BROKER_HEADER = 'kafka broker'
_TOPIC_HEADER = 'kafka topic operation'
_REQUIRED_BROKER_KEYS = ('bootstrap.servers', 'security.protocol', 'ssl.ca.location')
_REQUIRED_TOPIC_KEYS = ('name', 'partitions', 'replication_factor')

_KEY_CREATE_TOPICS = 'create_topics'
_KEY_UPDATE_TOPICS = 'update_topics'
_KEY_DELETE_TOPICS = 'delete_topics'
_TOPIC_CONFIG_OPERATION_KEYS = [_KEY_CREATE_TOPICS, _KEY_UPDATE_TOPICS, _KEY_DELETE_TOPICS]
_CREATE_OPERATION = 'CREATE'
_UPDATE_OPERATION = 'UPDATE'
_DELETE_OPERATION = 'DELETE'
_TOPIC_CONFIG_OPERATIONS = [_CREATE_OPERATION, _UPDATE_OPERATION, _DELETE_OPERATION]
_DEFAULT_BROKER_CONFIG = {'bootstrap.servers': 'localhost:9092'}


def load_broker_config(config_file):
    global broker_config

    logger.info(logging_codes.WHI_CAF_KAFKA_LIB_LOAD_CONFIG, config_file)
    config = configreader.load_config(config_file)
    configreader.validate_config(config, _BROKER_HEADER, _REQUIRED_BROKER_KEYS)
    broker_config = {**_DEFAULT_BROKER_CONFIG, **config[_BROKER_HEADER]}


def load_topic_config(config_file, topic_operation):
    global create_topic_list
    global update_topic_list
    global delete_topic_list
    logger.info(logging_codes.WHI_CAF_KAFKA_LIB_LOAD_CONFIG, config_file)
    config = configreader.load_config(config_file)
    configreader.validate_config(config, _TOPIC_HEADER, _TOPIC_CONFIG_OPERATION_KEYS)
    if topic_operation == _CREATE_OPERATION:
        _load_topic_list(config, create_topic_list, _KEY_CREATE_TOPICS)
    if topic_operation == _UPDATE_OPERATION:
        _load_topic_list(config, update_topic_list, _KEY_UPDATE_TOPICS)
    if topic_operation == _DELETE_OPERATION:
        _load_topic_list(config, delete_topic_list, _KEY_DELETE_TOPICS)


def _load_topic_list(configfile, topic_list, operation_header):
    for topic in configfile[_TOPIC_HEADER][operation_header].split(","):
        configreader.validate_config(configfile, topic, _REQUIRED_TOPIC_KEYS)
        topic_list.append(configfile[topic])


broker_config_path = os.getenv('CAF_KAFKA_BROKER_CONFIG_FILE', default='/var/app/config/caf-kafka.cfg')
topic_config_path = os.getenv('CAF_KAFKA_TOPIC_CONFIG_FILE', default='/var/app/config/caf-kafka-topics.cfg')
topic_config_operation = os.getenv('CAF_KAFKA_TOPIC_OPERATION',
                                   default='CREATE')  # CREATE, UPDATE or DELETE are valid values

if (broker_config_path or topic_config_path) is None:
    logger.warn(logging_codes.WHI_CAF_KAFKA_LIB_MISSING_CONFIG_ENV, 'CAF_KAFKA_BROKER_CONFIG_FILE',
                'CAF_KAFKA_TOPIC_CONFIG_FILE')
elif not (os.path.exists(broker_config_path) and os.path.isfile(broker_config_path) and os.path.exists(
        topic_config_path)) or not os.path.isfile(topic_config_path):
    logger.warn(logging_codes.WHI_CAF_KAFKA_LIB_MISSING_CONFIG_FILE)
    broker_config = _DEFAULT_BROKER_CONFIG
else:
    if topic_config_operation not in _TOPIC_CONFIG_OPERATIONS:
        logger.warn(logging_codes.WHI_CAF_KAFKA_LIB_INVALID_OPERATION, topic_config_operation)
    else:
        load_broker_config(broker_config_path)
        load_topic_config(topic_config_path, topic_config_operation)
