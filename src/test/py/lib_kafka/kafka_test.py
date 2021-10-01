import importlib
import os
from unittest import mock
from unittest.mock import MagicMock
from lib_kafka import logging_codes
import unittest
import concurrent.futures
from confluent_kafka.admin import ClusterMetadata, TopicMetadata, PartitionMetadata
from confluent_kafka import KafkaError, KafkaException


def get_sample_config_path(file_name):
    package_directory = os.path.dirname(os.path.abspath(__file__))
    root_path = "/../../../../sample_config"
    return os.path.join(package_directory + root_path, file_name)


class TestKafkaApiMethods(unittest.TestCase):

    def setUp(self) -> None:
        os.environ["KAFKA_BROKER_CONFIG_FILE"] = get_sample_config_path('kafka.env')
        os.environ["KAFKA_TOPIC_CONFIG_FILE"] = get_sample_config_path('kafka-topic.json')
        self.kafka = importlib.import_module('lib_kafka.kafka')

    @mock.patch("sys.exit")
    @mock.patch("confluent_kafka.admin.AdminClient.create_topics")
    def test_create_topics(self, mock_create_topics, mock_sys_exit):
        self.kafka.create_topics()
        self.assertTrue(mock_create_topics.called)
        self.assertEqual(mock_create_topics.call_count, 1)

        mock_create_topics.reset_mock()
        f = concurrent.futures.Future()
        f.set_running_or_notify_cancel()
        f.set_result(None)
        mock_create_topics.return_value = {'testTopic1': None, 'testTopic2': f}

        with self.assertLogs('lib_kafka.kafka', level='ERROR') as cm:
            self.kafka.create_topics()
            self.assertTrue(mock_create_topics.called)
            self.assertEqual(mock_create_topics.call_count, 1)
            self.assertTrue(mock_sys_exit.called)
            self.assertTrue(len(cm.output) > 0)

        mock_create_topics.reset_mock()
        kafka_error = MagicMock()
        kafka_error.code.return_value = KafkaError.TOPIC_ALREADY_EXISTS
        f.result = MagicMock(side_effect=KafkaException(kafka_error))
        mock_create_topics.return_value = {'testTopic1': f}

        with self.assertLogs('lib_kafka.kafka', level='INFO') as cm:
            self.kafka.create_topics()
            self.assertTrue(mock_create_topics.called)
            self.assertEqual(mock_create_topics.call_count, 1)
            self.assertTrue('INFO:lib_kafka.kafka:' + logging_codes.TOPIC_EXISTS % 'testTopic1' in cm.output)

        mock_create_topics.reset_mock()
        kafka_error = MagicMock()
        kafka_error.code.return_value = KafkaError._TIMED_OUT
        f.result = MagicMock(side_effect=KafkaException(kafka_error))
        mock_create_topics.return_value = {'testTopic1': f}

        with self.assertLogs('lib_kafka.kafka', level='ERROR') as cm:
            self.kafka.create_topics()
            self.assertTrue(mock_create_topics.called)
            self.assertEqual(mock_create_topics.call_count, 1)
            self.assertTrue(mock_sys_exit.called)
            self.assertTrue(len(cm.output) > 0)

        mock_create_topics.reset_mock()
        kafka_error = MagicMock()
        kafka_error.code.return_value = KafkaError.CLUSTER_AUTHORIZATION_FAILED
        f.result = MagicMock(side_effect=KafkaException(kafka_error))
        mock_create_topics.return_value = {'testTopic1': f}
        with self.assertLogs('lib_kafka.kafka', level='ERROR') as cm:
            self.kafka.create_topics()
            self.assertTrue(mock_create_topics.called)
            self.assertEqual(mock_create_topics.call_count, 1)
            self.assertTrue(mock_sys_exit.called)
            self.assertTrue(len(cm.output) > 0)

        mock_create_topics.reset_mock()
        f.result = MagicMock(side_effect=Exception)
        mock_create_topics.return_value = {'testTopic1': f}
        with self.assertLogs('lib_kafka.kafka', level='ERROR') as cm:
            self.kafka.create_topics()
            self.assertTrue(mock_create_topics.called)
            self.assertEqual(mock_create_topics.call_count, 1)
            self.assertTrue(mock_sys_exit.called)
            self.assertTrue(len(cm.output) > 0)

        mock_create_topics.reset_mock()

    @mock.patch("sys.exit")
    @mock.patch("confluent_kafka.admin.AdminClient.delete_topics")
    def test_delete_topic(self, mock_delete_topics, mock_sys_exit):
        # Topic delete successful
        mock_delete_topics.reset_mock()
        f = concurrent.futures.Future()
        f.set_running_or_notify_cancel()
        f.set_result(None)
        mock_delete_topics.return_value = {'testTopic': f}
        with self.assertLogs('lib_kafka.kafka', level='INFO') as cm:
            self.kafka.delete_topics()
            self.assertTrue(mock_delete_topics.called)
            self.assertEqual(mock_delete_topics.call_count, 1)
            self.assertTrue(
                'INFO:lib_kafka.kafka:' + logging_codes.DELETE_TOPIC_SUCCESS % 'testTopic' in cm.output)

        mock_delete_topics.reset_mock()
        f.result = MagicMock(side_effect=Exception)
        mock_delete_topics.return_value = {'testTopic': f}
        with self.assertLogs('lib_kafka.kafka', level='ERROR') as cm:
            self.kafka.delete_topics()
            self.assertTrue(mock_delete_topics.called)
            self.assertEqual(mock_delete_topics.call_count, 1)
            self.assertTrue(mock_delete_topics.called)
            self.assertTrue(mock_sys_exit.called)
            self.assertTrue(len(cm.output) > 0)

        mock_delete_topics.reset_mock()

    @mock.patch("confluent_kafka.admin.AdminClient.create_topics")
    @mock.patch("confluent_kafka.admin.AdminClient.delete_topics")
    @mock.patch("confluent_kafka.admin.AdminClient.create_partitions")
    @mock.patch("confluent_kafka.admin.AdminClient.list_topics")
    def test_update_partitions(self, mock_list_topics, mock_create_partitions,
                               mock_delete_topics, mock_create_topics):
        cluster_data1 = ClusterMetadata()
        topic_data1 = TopicMetadata()
        partition_data1 = PartitionMetadata()
        partition_data1.replicas = [0]
        topic_data1.topic = 'topic1'
        topic_data1.partitions = {0: partition_data1}
        cluster_data1.topics = {'topic1': topic_data1}

        mock_list_topics.return_value = cluster_data1
        self.kafka.update_topic_list = [
            {'name': 'topic1', 'partitions': 1, 'replication_factors': 1, 'recreate_topic': False}]
        # Same number of partitions as existing

        with self.assertLogs('lib_kafka.kafka', level='INFO') as cm:
            self.kafka.update_topics()
            self.assertTrue(mock_list_topics.called)
            self.assertEqual(mock_list_topics.call_count, 1)
            self.assertTrue(
                'INFO:lib_kafka.kafka:' + logging_codes.PARTITION_NUM_EQUAL % (1, 1, 'topic1') in cm.output)

        mock_list_topics.reset_mock()
        self.kafka.update_topic_list = [
            {'name': 'topic1', 'partitions': 2, 'replication_factors': 1, 'recreate_topic': False}]
        f = concurrent.futures.Future()
        f.set_running_or_notify_cancel()
        f.set_result(None)
        mock_create_partitions.return_value = {'topic1': f}
        with self.assertLogs('lib_kafka.kafka', level='INFO') as cm:
            self.kafka.update_topics()
            self.assertTrue(mock_list_topics.called)
            self.assertEqual(mock_list_topics.call_count, 1)
            self.assertTrue(mock_create_partitions.called)
            self.assertEqual(mock_create_partitions.call_count, 1)
            self.assertTrue(
                'INFO:lib_kafka.kafka:' + logging_codes.ADD_PARTITION_SUCCESS % ('topic1', 2) in cm.output)

        # Increase number of partitions - success
        mock_create_partitions.reset_mock()
        mock_create_partitions.return_value = {'testTopic1': None, 'testTopic2': f}

        with self.assertLogs('lib_kafka.kafka', level='INFO') as cm:
            self.kafka.update_topics()
            self.assertTrue(
                'INFO:lib_kafka.kafka:' + logging_codes.ADD_PARTITION_SUCCESS % ('testTopic2', 2) in cm.output)

            self.assertTrue(
                any('ERROR:lib_kafka.kafka:' in s for s in cm.output))

        # Decrease number of partitions with recreate topic true
        self.kafka.update_topic_list = [
            {'name': 'topic1', 'partitions': 0, 'replication_factors': 1, 'recreate_topic': True}]
        self.kafka.update_topics()
        self.assertTrue(mock_delete_topics.called)
        self.assertTrue(mock_create_topics.called)

        # Decrease number of partitions with recreate topic False
        self.kafka.update_topic_list = [
            {'name': 'topic1', 'partitions': 0, 'replication_factors': 1, 'recreate_topic': False}]
        mock_delete_topics.reset_mock()
        mock_create_topics.reset_mock()
        self.kafka.update_topics()
        self.assertFalse(mock_delete_topics.called)
        self.assertFalse(mock_create_topics.called)

        # Topic does not exist
        self.kafka.update_topic_list = [
            {'name': 'topic2', 'partitions': 0, 'replication_factors': 1, 'recreate_topic': False}]

        with self.assertLogs('lib_kafka.kafka', level='INFO') as cm:
            self.kafka.update_topics()
            self.assertTrue(
                'INFO:lib_kafka.kafka:' + logging_codes.TOPIC_NOT_FOUND % 'topic2' in cm.output)

    def test_convert_to_bool(self):
        self.assertFalse(self.kafka._convert_to_bool(None))
        self.assertFalse(self.kafka._convert_to_bool(''))
        self.assertFalse(self.kafka._convert_to_bool('  '))
        self.assertFalse(self.kafka._convert_to_bool('False'))
        self.assertFalse(self.kafka._convert_to_bool('None'))
        self.assertTrue(self.kafka._convert_to_bool('True'))
        self.assertTrue(self.kafka._convert_to_bool('TRUE'))


if __name__ == '__main__':
    unittest.main()
