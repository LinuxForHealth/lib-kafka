import os
import pytest
from pydantic import ValidationError
from lib_kafka import config as configuration
import importlib


@pytest.fixture(autouse=True)
def reset():
    reset_env_vars()


def reset_env_vars():
    for env_var in ("KAFKA_BROKER_CONFIG_FILE", "KAFKA_TOPIC_CONFIG_FILE"):
        if env_var in os.environ:
            del os.environ[env_var]


def get_sample_config_path(file_name):
    package_directory = os.path.dirname(os.path.abspath(__file__))
    root_path = "/../../../../sample_config"
    return os.path.join(package_directory + root_path, file_name)


def test_kafka_settings_success_object():
    settings = configuration.KafkaSettings(
        bootstrap_servers='test_server',
        group_id='test_group_id',
        security_protocol='test_protocol',
        enable_auto_commit=False,
        ssl_ca_location='test-location'
    )

    assert settings is not None


def test_kafka_settings_success_env_file():
    os.environ["KAFKA_BROKER_CONFIG_FILE"] = get_sample_config_path('kafka.env')
    importlib.reload(configuration)
    settings = configuration.KafkaSettings()
    assert settings is not None
    settings_dict = settings.dict(by_alias=True)
    assert 'bootstrap.servers' in settings_dict.keys() and settings_dict['bootstrap.servers'] == 'localhost:9093'
    assert 'group.id' in settings_dict.keys() and settings_dict['group.id'] == 'kafka-listener'
    assert 'security.protocol' in settings_dict.keys() and settings_dict['security.protocol'] == 'PLAINTEXT'
    assert 'ssl.ca.location' in settings_dict.keys() and settings_dict[
        'ssl.ca.location'] == '/var/app/certs/kafka/tls.crt'
    assert 'enable.auto.commit' in settings_dict.keys() and not settings_dict['enable.auto.commit']


def test_kafka_settings_failures():
    with pytest.raises(ValidationError):
        test_object = configuration.KafkaSettings(
            bootstrap_servers='test_server',
            group_id='test_group_id',
            security_protocol='test_protocol',
        )

        with pytest.raises(ValidationError):
            test_object = configuration.KafkaSettings(
                bootstrap_servers='test_server',
                group_id='test_group_id',
                security_protocol='test_protocol',
                enable_auto_commit=False
            )

        with pytest.raises(ValidationError):
            test_object = configuration.KafkaSettings(
                bootstrap_servers='test_server',
                group_id=32,
                security_protocol='test_protocol',
                enable_auto_commit=False,
                ssl_ca_location='test-location'
            )


def test_kafka_topics_success_parse():
    topics = configuration.KafkaTopics.parse_file(get_sample_config_path('kafka-topic.json'))
    assert topics is not None
    assert len(topics.dict()['__root__']) == 3


def test_kafka_topic_success_object():
    topic = configuration.KafkaTopic(
        name='test-topic',
        replication_factor=2,
        partitions=2,
        recreate_topic=False,
        operation=configuration.OperationEnum.create

    )

    assert topic is not None
    assert topic.name == 'test-topic'


def test_kafka_topic_failure_object():
    with pytest.raises(KeyError):
        topic = configuration.KafkaTopic(
            name='test-topic',
            replication_factor='non-int',
            partitions=2,
            recreate_topic=False,
            operation=configuration.OperationEnum.create
        )
