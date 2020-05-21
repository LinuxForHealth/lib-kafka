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
import unittest
import caf_logger.logger as caflogger
import importlib

from logging import CRITICAL

from whi_caf_lib_kafka import config
from whi_caf_lib_kafka.config import InvalidConfigException

test_broker_config_file_name = 'test_broker_config.ini'
test_topic_config_file_name = 'test_topic_config.ini'
test_broker_file_name_non_exist = 'non_exist.ini'
test_broker_without_kafka_header = 'test_broker_without_header_config.ini'
test_topic_config_file_name_exception = 'exception.ini'
test_broker_missingKeys = 'missingKeys.ini'
test_config_missingKeys = 'missing_config_keys.ini'
test_config_missingKeys_operation = 'missing_config_keys_operation.ini'

def get_resource_path(file_name):
    package_directory = os.path.dirname(os.path.abspath(__file__))
    root_path = "/../../resources"
    file = os.path.join(package_directory + root_path, file_name)
    print(file+" is the path name")
    return file


def setup_env_variable(config_kafka_broker_file_path, config_kafka_topic_config_file_path):
    os.environ['CAF_KAFKA_BROKER_CONFIG_FILE'] = config_kafka_broker_file_path
    os.environ['CAF_KAFKA_TOPIC_CONFIG_FILE'] = config_kafka_topic_config_file_path



class TestConfigMethods(unittest.TestCase):
    def setUp(self) -> None:
        test_config_broker_without_kafka_header = configparser.ConfigParser()
        test_config_broker_without_kafka_header.add_section('test')
        test_config_broker_without_kafka_header.set('test', 'test1', 'test2')
        test_config_broker_without_kafka_header.set('test', 'test3', 'test4')
        test_config_broker_without_kafka_header.set('test', 'test5', 'test6')
        with open(test_broker_without_kafka_header, 'w') as broker_exception_config_file:
            test_config_broker_without_kafka_header.write(broker_exception_config_file)

        test_missingKeys = configparser.ConfigParser()
        test_missingKeys.add_section('kafka broker')
        test_missingKeys.set('kafka broker', 'test1', 'test2')
        test_missingKeys.set('kafka broker', 'test3', 'test4')
        test_missingKeys.set('kafka broker', 'test5', 'test6')
        with open(test_broker_missingKeys, 'w') as broker_missingKeys_exception_file:
            test_missingKeys.write(broker_missingKeys_exception_file)

        test_config_broker = configparser.ConfigParser()
        test_config_broker.add_section('kafka broker')
        test_config_broker.set('kafka broker', 'bootstrap.servers', 'localhost:9093')
        test_config_broker.set('kafka broker', 'security.protocol', 'test')
        test_config_broker.set('kafka broker', 'ssl.ca.location', 'temp')
        with open(test_broker_config_file_name, 'w') as broker_config_file:
            test_config_broker.write(broker_config_file)
        test_config_topic = configparser.ConfigParser()
        test_config_topic.add_section('kafka topic operation')
        test_config_topic.set('kafka topic operation', 'create_topics', 'testTopic1,testTopic2')
        test_config_topic.set('kafka topic operation', 'update_topics', 'testTopic1,testTopic3')
        test_config_topic.set('kafka topic operation', 'delete_topics', 'testTopic2,testTopic3')
        test_config_topic.add_section('testTopic1')
        test_config_topic.set('testTopic1', 'name', 'testTopic1')
        test_config_topic.set('testTopic1', 'partitions', '1')
        test_config_topic.set('testTopic1', 'replication_factor', '1')
        test_config_topic.add_section('testTopic2')
        test_config_topic.set('testTopic2', 'name', 'testTopic2')
        test_config_topic.set('testTopic2', 'partitions', '1')
        test_config_topic.set('testTopic2', 'replication_factor', '1')
        test_config_topic.add_section('testTopic3')
        test_config_topic.set('testTopic3', 'name', 'testTopic3')
        test_config_topic.set('testTopic3', 'partitions', '1')
        test_config_topic.set('testTopic3', 'replication_factor', '1')
        with open(test_topic_config_file_name, 'w') as topic_config_file:
            test_config_topic.write(topic_config_file)

        test_config_topic_missingKeys = configparser.ConfigParser()
        test_config_topic_missingKeys.add_section('kafka topic operation')
        test_config_topic_missingKeys.set('kafka topic operation', 'create_topics', 'testTopic1')
        test_config_topic_missingKeys.set('kafka topic operation', 'update_test', 'testTopic1')
        test_config_topic_missingKeys.set('kafka topic operation', 'delete_test', 'testTopic1')
        test_config_topic_missingKeys.add_section('testTopic1')
        test_config_topic_missingKeys.set('testTopic1', 'test', 'testTopic1')
        test_config_topic_missingKeys.set('testTopic1', 'test', '1')
        test_config_topic_missingKeys.set('testTopic1', 'test', '1')

        with open(test_config_missingKeys, 'w') as topic_config_file_missingKeys:
            test_config_topic_missingKeys.write(topic_config_file_missingKeys)

        test_config_topic_missingKeys_operation = configparser.ConfigParser()
        test_config_topic_missingKeys_operation.add_section('kafka topic operation')
        test_config_topic_missingKeys_operation.set('kafka topic operation', 'create_test', 'testTopic1')
        test_config_topic_missingKeys_operation.set('kafka topic operation', 'update_test', 'testTopic1')
        test_config_topic_missingKeys_operation.set('kafka topic operation', 'delete_test', 'testTopic1')
        with open(test_config_missingKeys_operation, 'w') as topic_config_file_missingKeys_operation:
            test_config_topic_missingKeys_operation.write(topic_config_file_missingKeys_operation)


    def test_load_broker_config(self):
        config.config = None
        config.load_broker_config(test_broker_config_file_name)
        self.assertIsNotNone(config.broker_config)
        self.assertEqual(config.broker_config["bootstrap.servers"], 'localhost:9093')

        # Non existing file
        with self.assertRaises(InvalidConfigException) as ex:
            config.load_broker_config(test_broker_file_name_non_exist)

        #broker header not found
        with self.assertRaises(InvalidConfigException) as ex1:
            config.load_broker_config(test_broker_without_kafka_header)


        # Missing keys
        with self.assertRaises(InvalidConfigException) as ex1:
            config.load_broker_config(test_broker_missingKeys)




    def test_load_topic_config(self):
        config.create_topic_list = []
        config.update_topic_list = []
        config.delete_topic_list = []
        config.load_topic_config(test_topic_config_file_name, 'CREATE')
        self.assertEqual(len(config.create_topic_list), 2)
        self.assertEqual(config.create_topic_list[0]['name'], 'testTopic1')
        self.assertEqual(config.create_topic_list[1]['name'], 'testTopic2')
        self.assertEqual(len(config.update_topic_list), 0)
        self.assertEqual(len(config.delete_topic_list), 0)

        # load update topic list
        config.create_topic_list = []
        config.update_topic_list = []
        config.delete_topic_list = []
        config.load_topic_config(test_topic_config_file_name, 'UPDATE')
        self.assertEqual(len(config.create_topic_list), 0)
        self.assertEqual(len(config.update_topic_list), 2)
        self.assertEqual(config.update_topic_list[0]['name'], 'testTopic1')
        self.assertEqual(config.update_topic_list[1]['name'], 'testTopic3')
        self.assertEqual(len(config.delete_topic_list), 0)

        # load delete topic list
        config.create_topic_list = []
        config.update_topic_list = []
        config.delete_topic_list = []
        config.load_topic_config(test_topic_config_file_name, 'DELETE')
        self.assertEqual(len(config.create_topic_list), 0)
        self.assertEqual(len(config.update_topic_list), 0)
        self.assertEqual(len(config.delete_topic_list), 2)
        self.assertEqual(config.delete_topic_list[0]['name'], 'testTopic2')
        self.assertEqual(config.delete_topic_list[1]['name'], 'testTopic3')


        #invalid config exception
        with self.assertRaises(InvalidConfigException) as ex:
            config.load_topic_config(test_topic_config_file_name_exception,'TEST')

        #
        with self.assertRaises(InvalidConfigException) as ex:
            config.load_topic_config(test_config_missingKeys,'CREATE')

        with self.assertRaises(InvalidConfigException) as ex:
            config.load_topic_config(test_config_missingKeys_operation,'CREATE')

        with self.assertRaises(InvalidConfigException) as ex:
            config.load_topic_config(test_config_missingKeys_operation,'TEST')

        config.broker_config_path = None


    def tearDown(self) -> None:
        os.remove(test_broker_config_file_name)
        os.remove(test_topic_config_file_name)
