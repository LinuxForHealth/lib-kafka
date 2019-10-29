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

from logging import CRITICAL
from unittest import mock
from whi_caf_lib_kafka import kafka
import unittest
import concurrent.futures
from confluent_kafka.admin import ClusterMetadata, TopicMetadata, PartitionMetadata
import os


class TestKafkaApiMethods(unittest.TestCase):

    @mock.patch("confluent_kafka.admin.AdminClient.create_topics")
    @mock.patch("caf_logger.logger.CAFLogger.error")
    @mock.patch("caf_logger.logger.CAFLogger.info")
    def test_create_topics(self, mock_logger_info, mock_logger_error, mock_create_topics):
        kafka.create_topics()
        self.assertTrue(mock_create_topics.called)
        self.assertFalse(mock_logger_error.called)
        self.assertEqual(mock_create_topics.call_count, 1)

        f = concurrent.futures.Future()
        f.set_running_or_notify_cancel()
        f.set_result(None)
        mock_create_topics.return_value = {'testTopic1': None, 'testTopic2': f}
        kafka.create_topics()
        self.assertTrue(mock_create_topics.called)
        self.assertEqual(mock_create_topics.call_count, 2)
        self.assertTrue(mock_logger_error.called)
        self.assertTrue(mock_logger_info.called)

    @mock.patch("confluent_kafka.admin.AdminClient.delete_topics")
    @mock.patch("caf_logger.logger.CAFLogger.error")
    @mock.patch("caf_logger.logger.CAFLogger.info")
    def test_delete_topic(self, mock_logger_info, mock_logger_error, mock_delete_topics):
        kafka.delete_topics()
        self.assertTrue(mock_delete_topics.called)
        self.assertFalse(mock_logger_error.called)
        self.assertEqual(mock_delete_topics.call_count, 1)

        # Topic delete successful
        mock_delete_topics.reset_mock()
        f = concurrent.futures.Future()
        f.set_running_or_notify_cancel()
        f.set_result(None)
        mock_delete_topics.return_value = {'testTopic': f}
        kafka.delete_topics()
        self.assertTrue(mock_delete_topics.called)
        self.assertEqual(mock_delete_topics.call_count, 1)
        self.assertTrue(mock_logger_info.called)

    @mock.patch("confluent_kafka.admin.AdminClient.create_topics")
    @mock.patch("confluent_kafka.admin.AdminClient.delete_topics")
    @mock.patch("confluent_kafka.admin.AdminClient.create_partitions")
    @mock.patch("confluent_kafka.admin.AdminClient.list_topics")
    @mock.patch("caf_logger.logger.CAFLogger.error")
    @mock.patch("caf_logger.logger.CAFLogger.info")
    def test_update_partitions(self, mock_logger_info, mock_logger_error, mock_list_topics, mock_create_partitions,
                               mock_delete_topics, mock_create_topics):
        cluster_data1 = ClusterMetadata()
        topic_data1 = TopicMetadata()
        partition_data1 = PartitionMetadata()
        partition_data1.replicas = [0]
        topic_data1.topic = 'topic1'
        topic_data1.partitions = {0: partition_data1}
        cluster_data1.topics = {'topic1': topic_data1}

        mock_list_topics.return_value = cluster_data1
        kafka.update_topic_list = [{'name': 'topic1', 'partitions': 1, 'replication_factors': 1}]
        # Same number of partitions as existing
        kafka.update_topics(recreate_topic=False)
        self.assertEqual(mock_logger_info.call_count, 1)

        kafka.update_topic_list = [{'name': 'topic1', 'partitions': 2, 'replication_factors': 1}]
        # Increase number of partitions
        kafka.update_topics(recreate_topic=False)
        self.assertTrue(mock_create_partitions.called)

        # Increase number of partitions - success
        mock_create_partitions.reset_mock()
        mock_logger_info.reset_mock()
        f = concurrent.futures.Future()
        f.set_running_or_notify_cancel()
        f.set_result(None)
        mock_create_partitions.return_value = {'testTopic1': None, 'testTopic2': f}
        kafka.update_topics(recreate_topic=False)
        self.assertEqual(mock_logger_info.call_count, 1)

        # Increase number of partitions - Error
        self.assertEqual(mock_logger_error.call_count, 1)

        # Decrease number of partitions with recreate topic true
        kafka.update_topic_list = [{'name': 'topic1', 'partitions': 0, 'replication_factors': 1}]
        kafka.update_topics(recreate_topic=True)
        self.assertTrue(mock_delete_topics.called)
        self.assertTrue(mock_create_topics.called)

        # Decrease number of partitions with recreate topic False
        mock_delete_topics.reset_mock()
        mock_create_topics.reset_mock()
        kafka.update_topics()
        self.assertFalse(mock_delete_topics.called)
        self.assertFalse(mock_create_topics.called)

        # Topic does not exist
        kafka.update_topic_list = [{'name': 'topic2', 'partitions': 0, 'replication_factors': 1}]
        mock_logger_info.reset_mock()
        kafka.update_topics()
        self.assertEqual(mock_logger_info.call_count, 1)


if __name__ == '__main__':
    unittest.main()
