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

WHI_CAF_KAFKA_LIB_INVALID_CONFIG_HEADER = ('CAFERR001', 'Invalid {} config. {} header not found')
WHI_CAF_KAFKA_LIB_INVALID_CONFIG_PARAMETER = ('CAFERR002', 'Invalid {} config. {} parameter not found')
WHI_CAF_KAFKA_LIB_MISSING_CONFIG_ENV = ('CAFWARN001', '{} or {} environment variables not defined. Loading default '
                                                     'config...')
WHI_CAF_KAFKA_LIB_MISSING_CONFIG_FILE = ('CAFWARN002', 'Config file not found. Loading default config...')

WHI_CAF_KAFKA_LIB_LOAD_CONFIG = ('CAFLOG001', 'loading config file {}')

WHI_CAF_KAFKA_LIB_CREATE_TOPIC_SUCCESS = ('CAFLOG002', 'Topic {} created successfully')
WHI_CAF_KAFKA_LIB_CREATE_TOPIC_FAIL = ('CAFERR003', 'Failed to create topic {}: {}')

WHI_CAF_KAFKA_LIB_DELETE_TOPIC_SUCCESS = ('CAFLOG003', 'Topic {} deleted successfully')
WHI_CAF_KAFKA_LIB_DELETE_TOPIC_FAIL = ('CAFERR004', 'Failed to delete topic {}: {}')

WHI_CAF_KAFKA_LIB_ADD_PARTITION_SUCCESS = ('CAFLOG004', 'Additional partitions created for topic {}')
WHI_CAF_KAFKA_LIB_ADD_PARTITION_FAIL = ('CAFERR005', 'Failed to add partitions to topic {}: {}')
WHI_CAF_KAFKA_LIB_PARTITION_NUM_EQUAL = ('CAFLOG005', 'Current partition size: {} is already equal to requested '
                                                      'partition size: {}')
WHI_CAF_KAFKA_LIB_PARTITION_NUM_LESS = ('CAFLOG006', 'Requested partition size: {} less than current size: {}')

WHI_CAF_KAFKA_LIB_PARTITION_NUM_LESS_AND_NOT_RECREATE = ('CAFLOG007', 'Partition cannot be reduced for a topic. For '
                                                                      'recreating a topic with new partition call '
                                                                      'this function with recreate_topic value as '
                                                                      'True')
WHI_CAF_KAFKA_LIB_PARTITION_NUM_LESS_AND_RECREATE = ('CAFLOG008', 'Recreating topic {}')
WHI_CAF_LIB_TOPIC_NOT_FOUND = ('CAFLOG009', 'Topic: {} NOT found!')
