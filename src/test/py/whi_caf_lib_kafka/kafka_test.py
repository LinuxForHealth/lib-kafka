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
from unittest.mock import MagicMock
from whi_caf_lib_kafka import kafka, logger
import unittest
from confluent_kafka.admin import AdminClient, NewTopic, NewPartitions, ConfigResource, ConfigSource


class TestKafkaApiMethods(unittest.TestCase):

    def setUp(self) -> None:
        logger.logging.disable(level=CRITICAL)

    @mock.patch("confluent_kafka.admin.AdminClient.create_topics")
    def test_create_topics(self, mock_create_topics):
        kafka.create_topics()
        self.assertTrue(mock_create_topics.called)
        self.assertEqual(mock_create_topics.call_count, 1)

        mock_create_topics.return_value = {'test': None}
        kafka.create_topics()
        self.assertTrue(mock_create_topics.called)

if __name__ == '__main__':
    unittest.main()
