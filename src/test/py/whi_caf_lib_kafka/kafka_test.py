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
from whi_caf_lib_kafka import kafka, logger
import unittest
import concurrent.futures
from confluent_kafka.admin import ClusterMetadata, TopicMetadata, PartitionMetadata


class TestKafkaApiMethods(unittest.TestCase):

    def setUp(self) -> None:
        logger.logging.disable(level=CRITICAL)

    @mock.patch("confluent_kafka.admin.AdminClient.create_topics")
    @mock.patch("whi_caf_lib_kafka.logger.logger.error")
    @mock.patch("whi_caf_lib_kafka.logger.logger.info")
    def test_create_topics(self, mock_logger_info, mock_logger_error, mock_create_topics):
        kafka.create_topic()
        self.assertTrue(mock_create_topics.called)
        self.assertFalse(mock_logger_error.called)
        self.assertEqual(mock_create_topics.call_count, 1)

        f = concurrent.futures.Future()
        f.set_running_or_notify_cancel()
        f.set_result(None)
        mock_create_topics.return_value = {'testTopic1': None, 'testTopic2': f}
        kafka.create_topic()
        self.assertTrue(mock_create_topics.called)
        self.assertEqual(mock_create_topics.call_count, 2)
        self.assertTrue(mock_logger_error.called)
        self.assertTrue(mock_logger_info.called)

    @mock.patch("confluent_kafka.admin.AdminClient.delete_topics")
    @mock.patch("whi_caf_lib_kafka.logger.logger.error")
    @mock.patch("whi_caf_lib_kafka.logger.logger.info")
    def test_delete_topic(self, mock_logger_info, mock_logger_error, mock_delete_topics):
        kafka.delete_topic('testTopic')
        self.assertTrue(mock_delete_topics.called)
        self.assertFalse(mock_logger_error.called)
        self.assertEqual(mock_delete_topics.call_count, 1)

        # Topic delete successful
        f = concurrent.futures.Future()
        f.set_running_or_notify_cancel()
        f.set_result(None)
        mock_delete_topics.return_value = {'testTopic': f}
        self.assertTrue(mock_delete_topics.called)
        self.assertEqual(mock_delete_topics.call_count, 1)
        self.assertTrue(mock_logger_info.called)

    @mock.patch("confluent_kafka.admin.AdminClient.create_topics")
    @mock.patch("confluent_kafka.admin.AdminClient.delete_topics")
    @mock.patch("confluent_kafka.admin.AdminClient.create_partitions")
    @mock.patch("confluent_kafka.admin.AdminClient.list_topics")
    @mock.patch("whi_caf_lib_kafka.logger.logger.error")
    @mock.patch("whi_caf_lib_kafka.logger.logger.info")
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

        # Same number of partitions as existing
        kafka.update_partition(topic_name='topic1', partition_size=1, recreate_topic=False)
        self.assertEqual(mock_logger_info.call_count, 2)

        # Increase number of partitions
        kafka.update_partition(topic_name='topic1', partition_size='2', recreate_topic=False)
        self.assertTrue(mock_create_partitions.called)

        # Decrease number of partitions
        kafka.update_partition(topic_name='topic1', partition_size='0', recreate_topic=True)
        self.assertTrue(mock_delete_topics.called)
        self.assertTrue(mock_create_topics.called)


if __name__ == '__main__':
    unittest.main()
