# *******************************************************************************
# IBM Watson Imaging Common Application Framework 3.0                         *
#                                                                             *
# IBM Confidential                                                            *
#                                                                             *
# OCO Source Materials                                                        *
#                                                                             *
# C Copyright IBM Corp. 2019                                                *
#                                                                             *
# The source code for this program is not published or otherwise              *
# divested of its trade secrets, irrespective of what has been                *
# deposited with the U.S. Copyright Office.                                   *
# ******************************************************************************/

# Info
TOPIC_START_CREATE = 'KAFLIBLOG001: Started creating topic...'
CREATE_TOPIC_SUCCESS = 'KAFLIBLOG002: Topic "%s" created successfully'
TOPIC_EXISTS = 'KAFLIBLOG003: Topic "%s" already exist!'
TOPIC_START_DELETE = 'KAFLIBLOG004: Started deleting topic...'
DELETE_TOPIC_SUCCESS = 'KAFLIBLOG005: Topic "%s" deleted successfully'
TOPIC_NOT_EXISTS = 'KAFLIBLOG006: Topic "%s" does not exist so it can not be deleted!'
TOPIC_START_UPDATE = 'KAFLIBLOG007: Started updating topic...'
TOPIC_NOT_FOUND = 'KAFLIBLOG008: Topic "%s" NOT found!'
PARTITION_NUM_EQUAL = 'KAFLIBLOG009: Current partition size: %s is already equal to requested partition size: %s for topic %s'
PARTITION_NUM_LESS = 'KAFLIBLOG010: Requested partition size: %s less than current size: %s for topic %s'
PARTITION_NUM_LESS_AND_NOT_RECREATE = 'KAFLIBLOG011: Partition cannot be reduced for a topic. For recreating a topic with new partition call this function with recreate_topic value as True'
PARTITION_NUM_LESS_AND_RECREATE = 'KAFLIBLOG012: Recreating topic "%s" with partition size: %s'
ADD_PARTITION_SUCCESS = 'KAFLIBLOG013: Additional partitions created for topic "%s". Total partition count is now: %s'
MONITOR_IS_PAUSED = 'KAFLIBLOG014: MONITOR: consumers are currently paused'
MONITOR_LOG = 'KAFLIBLOG015: MONITOR: total active listeners: %s'
STARTING_LISTENER = 'KAFLIBLOG016: Starting listener'
COMMITTING_MESSAGE = 'KAFLIBLOG017: Committing message'
MESSAGE_DELIVERED = 'KAFLIBLOG018: Message delivered'
MESSAGE_QUEUED = 'KAFLIBLOG019: Message queued, awaiting delivery confirmation'

# Error
CONFIG_VALIDATION_FAILED = "KAFLIBERR001: Config validation failed: %s"
CONNECTION_TIMEOUT = 'KAFLIBERR002: Connection to broker "%s" timed out while attempting to create topic "%s": %s'
CREATE_TOPIC_FAIL = 'KAFLIBERR003: Failed to create topic "%s": %s'
DELETE_TOPIC_FAIL = 'KAFLIBERR004: Failed to delete topic "%s": %s'
INVALID_MSG_TYPE = 'KAFLIBERR005: msg can only be of type bytes or string'
ADD_PARTITION_FAIL = 'KAFLIBERR006: Failed to add partitions to topic %s: %s'
NO_ACTIVE_LOOP = 'KAFLIBERR007: Invalid call to async producer. No active loop'
CONSUMER_NOT_INITIALIZED = 'KAFLIBERR008: Cannot start listening when consumer is not initialized'
CONSUMER_ERROR = 'KAFLIBERR009: Consumer error: %s'
PRODUCER_NOT_INITIALIZED = 'KAFLIBERR010: Cannot send message when producer is not initialized'

# Warn
PURGING_MESSAGE_SEGMENTS = 'KAFLIBWARN001: Purging message segments with identifier: %s'
LISTENER_EXITED = 'KAFLIBWARN002: Listener exited with exception: %s'
MESSAGE_DELIVERY_FAILED = 'KAFLIBWARN003: Message delivery failed: %s'
