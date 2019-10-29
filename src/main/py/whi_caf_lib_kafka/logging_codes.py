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

WHI_CAF_KAFKA_LIB_INVALID_CONFIG_HEADER = ('CAFKAFKALIBERR001', 'Invalid {} config. {} header not found')
WHI_CAF_KAFKA_LIB_INVALID_CONFIG_PARAMETER = ('CAFKAFKALIBERR002', 'Invalid {} config. {} parameter not found')
WHI_CAF_KAFKA_LIB_MISSING_CONFIG_ENV = ('CAFKAFKALIBWARN001', '{} or {} environment variables not defined. Loading '
                                                              'default config...')
WHI_CAF_KAFKA_LIB_MISSING_CONFIG_FILE = ('CAFKAFKALIBWARN002', 'Config file not found. Please check config file path '
                                                               'and name...')
WHI_CAF_KAFKA_LIB_INVALID_OPERATION = ('CAFKAFKALIBWARN003', 'Invalid Operation: {}. Supported operations are CREATE, '
                                                             'UPDATE or DELETE')
WHI_CAF_KAFKA_LIB_LOAD_CONFIG = ('CAFKAFKALIBLOG001', 'loading config file {}')

WHI_CAF_KAFKA_LIB_CREATE_TOPIC_SUCCESS = ('CAFKAFKALIBLOG002', 'Topic {} created successfully')
WHI_CAF_KAFKA_LIB_CREATE_TOPIC_FAIL = ('CAFKAFKALIBERR003', 'Failed to create topic {}: {}')

WHI_CAF_KAFKA_LIB_DELETE_TOPIC_SUCCESS = ('CAFKAFKALIBLOG003', 'Topic {} deleted successfully')
WHI_CAF_KAFKA_LIB_DELETE_TOPIC_FAIL = ('CAFKAFKALIBERR004', 'Failed to delete topic {}: {}')

WHI_CAF_KAFKA_LIB_ADD_PARTITION_SUCCESS = ('CAFKAFKALIBLOG004', 'Additional partitions created for topic {}')
WHI_CAF_KAFKA_LIB_ADD_PARTITION_FAIL = ('CAFKAFKALIBERR005', 'Failed to add partitions to topic {}: {}')
WHI_CAF_KAFKA_LIB_PARTITION_NUM_EQUAL = ('CAFKAFKALIBLOG005', 'Current partition size: {} is already equal to '
                                                              'requested partition size: {}')
WHI_CAF_KAFKA_LIB_PARTITION_NUM_LESS = ('CAFKAFKALIBLOG006', 'Requested partition size: {} less than current size: {}')

WHI_CAF_KAFKA_LIB_PARTITION_NUM_LESS_AND_NOT_RECREATE = ('CAFKAFKALIBLOG007', 'Partition cannot be reduced for a '
                                                                              'topic. For recreating a topic with new'
                                                                              ' partition call this function with '
                                                                              'recreate_topic value as True')
WHI_CAF_KAFKA_LIB_PARTITION_NUM_LESS_AND_RECREATE = ('CAFKAFKALIBLOG008', 'Recreating topic {}')
WHI_CAF_LIB_TOPIC_NOT_FOUND = ('CAFKAFKALIBLOG009', 'Topic: {} NOT found!')
