"""
@File:ConsumerUsage.py
@Author:lcx
@Date:2020/10/209:35
@Desc:消费者用例
"""
import os
import time

from EEGPlatformCommunicationModule4py.communicationModuleImplement.CommunicationConsumer import CommunicationConsumer
import uuid

from EEGPlatformCommunicationModule4py.communicationModuleInterface.CommunicationConsumerInterface import \
    CommunicationConsumerInterface

if __name__ == '__main__':

    father_path = os.path.dirname(__file__)
    # 消费者配置文件地址
    # 配置文件中"bootstrap.servers"为必填选项，格式为"[host]:[port]"，请务必在本机系统中将服务器ip映射至host中，
    # 在当前部署方式下，host名称务必为“server”，不要直接使用ip访问！
    # 不清楚kafka服务器地址和端口时请询问kafka服务器维护者
    conf_path = os.path.join(os.path.join(father_path, r"config"), 'consumer-config.json')
    # 收信topic名
    topic = "py-test-topic1"

    try:
        # 获得消费者实例
        # 该构造方法的第二个参数为消费者组名，本项目内约定，非特殊声明时，消费者组名应与消费者实例一一对应，即不允许多个消费者使用同一消费者组名
        # 使用者可用UUID之类的唯一标识符做消费者组名
        consumer: CommunicationConsumerInterface = CommunicationConsumer(conf_path, str(uuid.uuid1()))
        # 订阅收信topic
        consumer.subscribe(topic)
        # 循环接收消息
        while True:
            # 收信方法调用，当消费者在0.5s时限内能收到的消息时，consumeMsg为bytes()型，本例仅使用str()方法给出简单的反序列化示例，具体反序列化
            # 方法应由使用者决定
            consume_msg = consumer.receive()
            if consume_msg:
                print(str(consume_msg, encoding="utf-8"))
            else:
                print("no msg, get: {}".format(type(consume_msg)))
            time.sleep(1)
    except KeyboardInterrupt as ke:
        # 手动打断循环时关闭消费者实例以释放资源
        consumer.close()
