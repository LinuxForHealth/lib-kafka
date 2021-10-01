from unittest import mock
from lib_kafka import message_segmenter
import unittest
import uuid
import time


class TestMessageSegmenter(unittest.TestCase):

    def test_segment_message(self):
        msg = '0'*(1000*1024)
        all_results = list(message_segmenter.segment_message(msg))
        self.assertEqual(len(all_results), 2)               # total segments are 2
        self.assertEqual(len(all_results[0][0]), 900*1024)          # first segment is 900*1024 bytes
        self.assertEqual(all_results[0][1], all_results[1][1])      # identifier is equal for both
        self.assertEqual(all_results[0][2], all_results[1][2])      # count is equal for both
        self.assertEqual(all_results[1][2], b'2')       # count is 2
        self.assertEqual(all_results[0][3], b'1')       # index for first segment is 1
        self.assertEqual(all_results[1][3], b'2')       # index for second segment is 2

        msg = 'Hello World'
        all_results = list(message_segmenter.segment_message(msg, 5))
        self.assertEqual(len(all_results), 3)
        self.assertEqual(len(all_results[0][0]), 5)

        msg = b'Hello World'
        all_results = list(message_segmenter.segment_message(msg, 5))
        self.assertEqual(len(all_results), 3)
        self.assertEqual(len(all_results[0][0]), 5)

        try:
            list(message_segmenter.segment_message(5))
            self.fail('expected exception')
        except Exception as e:
            self.assertEqual(type(e), ValueError)

    def test_combine_segments(self):
        msgs = [b'hello', b' how ', b'are y', b'ou']
        index = 1
        identifier = str(uuid.uuid4()).encode('utf-8')
        count = b'4'
        for msg in msgs:
            result = message_segmenter.combine_segments(msg, {
                message_segmenter.ID: identifier,
                message_segmenter.COUNT: count,
                message_segmenter.INDEX: str(index).encode('utf-8')
            })
            index += 1
            if index <= 4:
                self.assertIsNone(result)
            else:
                self.assertIsNotNone(result)
                
        self.assertEqual(result, b'hello how are you')

    def test_purge_segements(self):
        message_segmenter._message_store['abcd'] = {
            'bitset': None,
            'segments': None,
            'last_accessed': time.time() - (10 * 60 - 1)
        }

        message_segmenter._purge_segments()
        self.assertEqual(len(message_segmenter._message_store), 1)

        time.sleep(2)

        message_segmenter._purge_segments()
        self.assertEqual(len(message_segmenter._message_store), 0)
        

if __name__ == '__main__':
    unittest.main()
