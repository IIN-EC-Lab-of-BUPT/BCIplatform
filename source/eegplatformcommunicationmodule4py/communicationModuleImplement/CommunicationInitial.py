"""
@File:CommunicationInitial.py
@Author:lcx
@Date:2020/10/714:38
@Desc:
"""
import json
import os

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.cimpl import KafkaException, KafkaError

from ..communicationModuleImplement.componentInterface.QueryInterface import QueryInterface
from ..communicationModuleInterface.CommunicationInitialInterface import CommunicationInitialInterface
from ..communicationModuleInterface.communicationModuleException import Exceptions


class CommunicationInitial(CommunicationInitialInterface):

    @staticmethod
    def topic_query(communication_character: QueryInterface) -> list:
        return communication_character.list_topics()

    @staticmethod
    def topic_create(topic: str, conf_path: str, num_partitions=1, replication_factor=1):
        retry_limit = 0
        if not os.path.exists(conf_path):
            raise Exceptions.NoConfigFileException("NoConfigFileException in {}".format(conf_path))
        with open(conf_path, 'r') as load_f:
            conf = json.load(load_f)
        if "bootstrap.servers" not in conf.keys():
            raise Exceptions.WrongConfigContextException("need bootstrap.servers")
        if "retry.limit" in conf.keys():
            retry_limit = int(conf["retry.limit"])
            conf.pop("retry.limit")

        retry_time = -1
        exception = None
        while retry_time < retry_limit:
            admin_client = AdminClient(conf)
            new_topics = [NewTopic(topic, num_partitions, replication_factor)]
            fs = admin_client.create_topics(new_topics)
            for topic, f in fs.items():
                try:
                    f.result(timeout=1)  # The result itself is None
                    return topic
                except KafkaException as ke:
                    # topic already exits.
                    if ke.args[0].code() == KafkaError.TOPIC_ALREADY_EXISTS:
                        return topic
                except Exception as e:
                    retry_time += 1
                    exception = e
        if exception:
            raise Exceptions.TopicCreateFailed(exception)

    @staticmethod
    def topic_delete(topic: str, conf_path: str):
        if not os.path.exists(conf_path):
            raise Exceptions.NoConfigFileException
        with open(conf_path, 'r') as load_f:
            conf = json.load(load_f)
        if not "bootstrap.servers" in conf.keys():
            raise Exceptions.WrongConfigContextException
        if "retry.limit" in conf.keys():
            conf.pop("retry.limit")
        admin_client = AdminClient(conf)
        fs = admin_client.delete_topics([topic], request_timeout=1)
        for topic, f in fs.items():
            try:
                f.result()  # The result itself is None
                return topic
            except Exception as e:
                raise Exceptions.TopicDeleteFailed(e)
