"""
@File:CommunicationConsumerInterface.py
@Author:lcx
@Date:2020/10/714:36
@Desc:
"""
from abc import ABCMeta, abstractmethod


class CommunicationConsumerInterface(metaclass=ABCMeta):

    @abstractmethod
    def subscribe(self, topic):
        pass

    @abstractmethod
    def unsubscribe(self):
        pass

    @abstractmethod
    def list_topics(self, topic=None, timeout=0.5):
        pass

    @abstractmethod
    def receive(self):
        pass

    @abstractmethod
    def timeStampReceive(self):
        pass

    @abstractmethod
    def close(self):
        pass
