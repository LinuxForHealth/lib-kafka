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

from logging import CRITICAL

from whi_caf_lib_kafka import config

test_broker_config_file_name = 'test_broker_config.ini'
test_topic_config_file_name = 'test_topic_config.ini'


class TestConfigMethods(unittest.TestCase):
    def setUp(self) -> None:
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

    def test_load_broker_config(self):
        config.config = None
        config.load_broker_config(test_broker_config_file_name)
        self.assertIsNotNone(config.broker_config)
        self.assertEqual(config.broker_config["bootstrap.servers"], 'localhost:9093')

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

    def tearDown(self) -> None:
        os.remove(test_broker_config_file_name)
        os.remove(test_topic_config_file_name)
