import time
from loguru import logger
from ctypes import *
CDLL(r"D:\Anaconda3\Lib\site-packages\confluent_kafka.libs\librdkafka-09f4f3ec.dll")

from AlgorithmSystem.AlgorithmSystemController import AlgorithmSystemControl
import sys


sys.path.append('.')


if __name__ == "__main__":
    date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    logger.add(sink=fr'./log/stimulation-system-{date}.log', level="INFO", retention='1 week')

    asc = AlgorithmSystemControl()
    asc.run()
