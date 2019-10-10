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

import logging
import logging.config
import os

package_directory = os.path.dirname(os.path.abspath(__file__))
LOGGING_FORMAT_STRING = '%(asctime)s - [%(name)s] - [%(threadName)s] - [%(levelname)s] - %(message)s'
logger = None


def init_logger(logging_config_file):
    global logger
    logging.config.fileConfig(logging_config_file)
    logger = logging.getLogger('whi-caf-lib-kafka')


logging_file = os.path.join(package_directory, "logging.conf")
init_logger(logging_file)
