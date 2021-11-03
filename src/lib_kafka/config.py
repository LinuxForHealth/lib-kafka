import os
from typing import List, Optional
from enum import Enum
from pydantic import BaseSettings, BaseModel, Field, validator

from lib_kafka import logger_util

TOPIC_OPERATION_KEY = 'operation'
logger = logger_util.get_logger(__name__)


class OperationEnum(str, Enum):
    create = "CREATE"
    update = "UPDATE"
    delete = "DELETE"


class KafkaTopic(BaseModel):
    name: str
    replication_factor: Optional[int]
    partitions: Optional[int]
    recreate_topic: Optional[bool]
    operation: OperationEnum

    @validator("operation", allow_reuse=True)
    def validate_operation(cls, v, values, **kwargs):
        if v == OperationEnum.create:
            if not values['partitions']:
                raise ValueError('partitions much be provided for ' + v + ' operation')
            if not values['replication_factor']:
                raise ValueError('replication_factor much be provided for ' + v + ' operation')

        if v == OperationEnum.update:
            if values['partitions'] is None:
                raise ValueError('partitions must be provided for ' + v + ' operation')
            if values['replication_factor'] is None:
                raise ValueError('replication_factor must be provided for ' + v + ' operation')
            if values['recreate_topic'] is None:
                raise ValueError('recreate_topic must be provided for ' + v + ' operation')

        return v


class KafkaTopics(BaseModel):
    __root__: List[KafkaTopic]


class KafkaSettings(BaseSettings):
    bootstrap_servers: str = Field(alias='bootstrap.servers', default='localhost:9092')
    group_id: str = Field(alias='group.id')
    security_protocol: str = Field(alias='security.protocol')
    ssl_ca_location: str = Field(alias='ssl.ca.location')
    enable_auto_commit: bool = Field(alias='enable.auto.commit', default=False)

    class Config:
        env_file: str = os.getenv('KAFKA_BROKER_CONFIG_FILE', default='/var/app/config/kafka.env')
        allow_population_by_field_name = True
