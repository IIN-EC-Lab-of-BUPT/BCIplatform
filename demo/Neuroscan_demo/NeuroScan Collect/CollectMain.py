from Starter import Collect
from ctypes import *
CDLL(r"D:\anaconda3\Lib\site-packages\confluent_kafka.libs\librdkafka-09f4f3ec.dll")


Device_confPath = r"./DeviceModule/config/NeuroScan.json"               #NeuroScan配置文件
confPath = r"./MessageQueue/usage/config/producer-config.json"             #kafka配置文件路径
initialPath = r"./MessageQueue/usage/config/Initial-config.json"           #kafka初始化路径


if __name__ == '__main__':
    collect = Collect(Device_confPath)
    collect.run(confPath,initialPath)