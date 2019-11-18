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
import caf_logger.logger as caflogger
from whi_caf_lib_kafka import logging_codes

logger = caflogger.get_logger('whi-caf-lib-kafka')

broker_config = None
create_topic_list = []
delete_topic_list = []
update_topic_list = []
broker_header = 'kafka broker'
topic_header = 'kafka topic operation'
broker_keys = ('bootstrap.servers', 'security.protocol', 'ssl.ca.location')
topic_keys = ('name', 'partitions', 'replication_factor')
topic_config_operation_keys = ('create_topics', 'delete_topics', 'update_topics')
topic_config_operations = ('CREATE', 'UPDATE', 'DELETE')
default_broker_config = {'bootstrap.servers': 'localhost:9092'}


class InvalidConfigException(Exception):
    pass


def load_broker_config(config_file):
    global broker_config
    broker_config = {}
    logger.info(logging_codes.WHI_CAF_KAFKA_LIB_LOAD_CONFIG, config_file)
    configfile = configparser.ConfigParser()
    configfile.optionxform = str
    configfile.read(config_file)
    if broker_header not in configfile.sections():
        logger.error(logging_codes.WHI_CAF_KAFKA_LIB_INVALID_CONFIG_HEADER, 'broker', 'kafka broker')
        raise InvalidConfigException('kafka broker header not found.')
    temp_config = configfile[broker_header]

    if not validate_broker_config(temp_config):
        raise InvalidConfigException('Missing keys')
    broker_config['bootstrap.servers'] = temp_config['bootstrap.servers']
    broker_config['security.protocol'] = temp_config['security.protocol']
    broker_config['ssl.ca.location'] = temp_config['ssl.ca.location']


def load_topic_config(config_file, topic_config_operation):
    global create_topic_list
    global update_topic_list
    global delete_topic_list
    logger.info(logging_codes.WHI_CAF_KAFKA_LIB_LOAD_CONFIG, config_file)
    configfile = configparser.ConfigParser()
    configfile.optionxform = str
    configfile.read(config_file)
    if topic_header not in configfile.sections():
        logger.error(logging_codes.WHI_CAF_KAFKA_LIB_INVALID_CONFIG_HEADER, 'topic', 'kafka topic operation')
        raise InvalidConfigException('kafka topic operation header not found.')

    if not validate_topic_operation_config(configfile[topic_header]):
        raise InvalidConfigException('Missing keys. Expected keys are create_topics, update_topics and '
                                     'delete_topics')
    if (topic_config_operation == 'CREATE') and ('create_topics' in configfile[topic_header]):
        _load_topic_list(configfile, create_topic_list, 'create_topics')
    if (topic_config_operation == 'UPDATE') and ('update_topics' in configfile[topic_header]):
        _load_topic_list(configfile, update_topic_list, 'update_topics')
    if (topic_config_operation == 'DELETE') and ('delete_topics' in configfile[topic_header]):
        _load_topic_list(configfile, delete_topic_list, 'delete_topics')


def _load_topic_list(configfile, topic_list, operation_header):
    for topic in configfile[topic_header][operation_header].split(","):
        if validate_topic_config(configfile[topic]):
            topic_list.append(configfile[topic])
        else:
            raise InvalidConfigException('Missing keys. Expected keys are name, partitions and '
                                         'replication_factor')


def validate_broker_config(config):
    valid = True
    for key in broker_keys:
        if key not in config:
            logger.error(logging_codes.WHI_CAF_KAFKA_LIB_INVALID_CONFIG_PARAMETER, 'broker', key)
            valid = False
    return valid


def validate_topic_config(config):
    valid = True
    for key in topic_keys:
        if key not in config.keys():
            logger.error(logging_codes.WHI_CAF_KAFKA_LIB_INVALID_CONFIG_PARAMETER, 'topic', key)
            valid = False
    return valid


def validate_topic_operation_config(config):
    for key in topic_config_operation_keys:
        if key in config.keys():
            return True
    return False


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
    broker_config = default_broker_config
else:
    if topic_config_operation not in topic_config_operations:
        logger.warn(logging_codes.WHI_CAF_KAFKA_LIB_INVALID_OPERATION, topic_config_operation)
    else:
        load_broker_config(broker_config_path)
        load_topic_config(topic_config_path, topic_config_operation)
