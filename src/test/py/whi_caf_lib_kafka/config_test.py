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

logger = caflogger.get_logger('whi-caf-lib-kafka')

test_broker_config_file_name = 'test_broker_config.ini'
test_topic_config_file_name = 'test_topic_config.ini'


class TestConfigMethods(unittest.TestCase):
    def setUp(self) -> None:
        test_config_broker = configparser.ConfigParser()
        test_config_broker.add_section('kafka broker')
        test_config_broker.set('kafka broker', 'bootstrap.servers', 'localhost:9093')
        with open(test_broker_config_file_name, 'w') as broker_config_file:
            test_config_broker.write(broker_config_file)
        test_config_topic = configparser.ConfigParser()
        test_config_topic.add_section('kafka topic')
        test_config_topic.set('kafka topic', 'topics', 'testTopic')
        test_config_topic.set('kafka topic', 'partitions', '2')
        test_config_topic.set('kafka topic', 'replication_factors', '1')
        with open(test_topic_config_file_name, 'w') as topic_config_file:
            test_config_topic.write(topic_config_file)

    def test_load_broker_config(self):
        config.config = None
        config.load_broker_config(test_broker_config_file_name)
        self.assertIsNotNone(config.broker_config)
        self.assertEqual(config.broker_config["bootstrap.servers"], 'localhost:9093')

    def test_load_topic_config(self):
        config.config = None
        config.load_topic_config(test_topic_config_file_name)
        self.assertIsNotNone(config.broker_config)
        self.assertEqual(config.topic_config["topics"], 'testTopic')
        self.assertEqual(config.topic_config["partitions"], '2')
        self.assertEqual(config.topic_config["replication_factors"], '1')

    def tearDown(self) -> None:
        os.remove(test_broker_config_file_name)
        os.remove(test_topic_config_file_name)
