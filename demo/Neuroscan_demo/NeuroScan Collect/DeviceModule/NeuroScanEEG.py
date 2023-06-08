#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
@Time : 2020/10/30 16:18
@Author : Nieeka
@Version：V 1.0
@File : NeuroScanEEG_raw.py
@Desciption :对NeuroScanEEG原始字节流直接处理
"""
import queue
import socket
import threading
import time
from loguru import logger
import numpy as np

from ctypes import *
CDLL(r"D:\anaconda3\Lib\site-packages\confluent_kafka.libs\librdkafka-09f4f3ec.dll")

from DeviceInterface.NeuroScanEEGInterface import NeuroScanEEGInterface
from EEGPlatformCommunicationModule4py.communicationModuleImplement.CommunicationInitial import CommunicationInitial
from EEGPlatformCommunicationModule4py.communicationModuleImplement.CommunicationProducer import CommunicationProducer
from NeuroScanMessage import NeuroScanMessage
import time
import sys
# np.set_printoptions(threshold=sys.maxsize);




class NeuroScanEEGThread(threading.Thread, NeuroScanEEGInterface, ):
    def __init__(self, threadName, device, n_chan, hostname, port, topic,loglevel):
        #调用Thread父类的初始化方法
        threading.Thread.__init__(self)
        self.name = threadName
        self.sock = []
        self.device = device
        self.n_chan = n_chan
        self.hostname = hostname
        self.port = port
        self.topic = topic
        self._update_interval = 0.04  # unit is seconds. eegthread sends TCP/IP socket in 40 milliseconds
        # cash 数据和event缓存
        self.event = None
        # package 是要发送的数据包
        self.package = None
        self.receivedataFlag=True
        self.openflag=True

        self.eventcount=0
        self.queue=queue.Queue()
        self.receiveThread=None
        self.sendThread=None
        self.level=loglevel
        if self.level == 0:
            self.logger=None
        else:
            self.logger = logger
            self.logger.add("Log/NeuroScanEEGtest_{time}.log", rotation="100MB", encoding="utf-8", enqueue=True,
                            compression="zip",
                            retention="1 days")
            self.logger.info('ConfiguratinInfo【DeviceName:{} Port:{} ChannelNumber:{} TopicName:{}】',device,port,n_chan,topic)


    def connect_kafka(self,initialPath,confPath):
        connecet_kafka = False
        while not connecet_kafka:
            try:
                CommunicationInitial.topicCreate(self.topic, initialPath)
                self.producer = CommunicationProducer(confPath)
                connecet_kafka = True
                if self.level==2:
                    self.logger.info('CONNECT TO Kafka')
            except:
                if self.level!=0:
                    self.logger.debug('CANNOT CONNECT TO Kafka')
                    time.sleep(0.5)

    def connect(self):
        """
        try to connect data server
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        notconnect = True
        reconnecttime = 0  # 未连接次数
        #尝试连接服务器
        while notconnect:
            try:
                #客服端连接到服务器
                self.sock.connect((self.hostname, self.port))
                notconnect = False
                if self.level!=0:
                    self.logger.info('DATA SERVER CONNECTED')
            except:
                reconnecttime += 1
                if self.level!=0:
                    if reconnecttime==1:
                        self.logger.info('CONNECT FAILED, RETRYING FOR {} TIME', reconnecttime)
                    if reconnecttime!= 1:
                        self.logger.info('CONNECT FAILED, RETRYING FOR {} TIMES', reconnecttime)
                if reconnecttime > 20:
                    break
        # self.shutdown_flag = threading.Event()
        # self.shutdown_flag.set()
        # self.sock.setblocking(True)
        return notconnect


    def run(self):
        """
        线程开始函数
        """

        self.read_thread()

    def read_thread(self):
        """
        visit eegthread, catch sockets and parse sockets, append parsed data to ringbuffer
        """
        # 请求获得基本信号：通道数目，采样率和数据包大小
        self.requestInfo()
        # 请求导联信息
        self.requestChannelInfo()
        time.sleep(1)
        self.receiveThread=threading.Thread(target=self.parseData)
        self.sendThread=threading.Thread(target=self.sendData)

        self.receiveThread.start()
        self.sendThread.start()



    #接收端线程
    def parseData(self):
        """
        handle data,message and event
        """
        while True:
            try:

                sendStartStreaming = NeuroScanMessage().startStreaming()
                # 还需要端口发送
                self.sock.send(sendStartStreaming)

                message, data = self.clientProcess(self.sock)
                print(message,data);
                timeIn = self.get_time_stamp()
                print('1')
                if self.info["eegChan"]==1:
                    raise Exception("new connection")


                # todo:raise Exception
                if self.info["eegChan"] != self.n_chan:
                    print(self.info["eegChan"])
                    print(self.n_chan)
                    print("channel数不匹配")
                    self.sock.close()
                    raise Exception("Channel error")

                if message['code'] == 2 and message["request"]==1 and self.receivedataFlag:
                    t="DATA"
                    data = self._unpackEEG(data)

                    # package是要发送的数据包
                    self.package = dict(
                        data=data,
                        startSample=message['startSample'],
                    )
                    print(t)

                elif message['code'] == 3 and message["request"]==1:
                    t="EVENT"
                    # event
                    eventType = data[0:4].copy().view(dtype=np.uint32)
                    startEvent = data[8:12].copy().view(dtype=np.uint32)
                    print(t)

                    if self.level !=0:
                        self.logger.info("received {} information，started at {}，type {}", t, startEvent, eventType)

                elif message["code"] == 4 and message["request"] == 1:
                    t="IMPEDANCE"
                    im_len = message["packetSize"]
                    impedance = data[0:im_len].copy().view(dtype=np.float32)
                    print(t)
                    print(impedance)

                elif message["code"] == 1 and message["request"] == 3:
                    t="TIPS"
                    print(t)
                    print("START TO RECEIVE IMPEDANCE")
                    self.receivedataFlag=False

                    continue

                elif message["code"] == 1 and message["request"] == 4:
                    t="TIPS"
                    print("IMPEDANCE RECEIVED")
                    self.receivedataFlag=True

                    continue

                else:
                    t="UNKNOWN"
                    print(t)
                    continue

                if self.package is None:
                    print("EMPTY DATA")
                    return None

                packet = self.package['data']
                # print(len(packet))
                startData = self.package['startSample']

                if self.level==2:
                    self.logger.info("received {} information，started at {}，received time {}", t, startData, timeIn)
                # add addtiontal channel if event exists
                #print('Received [{s}] kBytes of EEG Data,start at [{t}]'.format(s=str(len(packet) / 1000), t=startData))
                # shape为（10，500）
                print(packet,packet.shape)
                #time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                #现在会把event叠到数据上
                # wholePacket = self.downSample(np.concatenate((packet, events), axis=0))
                # wholePacket = self.downSample(packet)
                # print(packet)
                self.queue.put(packet)

            except Exception as e:
                print("错误类型为",e)
                time.sleep(0.01)
                notconnect = self.connect()

                if notconnect:
                    if self.level!=0:
                        self.logger.debug("Can't connect recorder, Please open the hostport ")
                    raise TypeError("Can't connect recorder, Please open the hostport ")

                # 请求获得基本信号：通道数目，采样率和数据包大小
                self.requestInfo()
                # 请求导联信息
                self.requestChannelInfo()

    #发送端线程
    def sendData(self):
        """
        send bytestream data to kafka
        """
        while True:
            if self.queue.qsize()>0:
                try:
                    wholePacket=self.queue.get()

                    packet = wholePacket.tobytes()
                    self.producer.send(self.topic, packet)  # 发送至Kafka
                    # self.logger.info('sendsendsend')


                except Exception as e:
                    print("错误类型为",e)
                    self.connect_kafka()



    def clientProcess(self,sock):
        headSize = 20
        head = sock.recv(headSize)
        head = np.frombuffer(head, dtype=np.uint8)
        print("head:",head)
        message = self._parseHeader(head)
        print("code:", message['code'], " request:", message["request"],"startsample:",message["startSample"],"packetsize:",message["packetSize"])
        if message["packetSize"]==0:
            print("包的大小为0")
         #根据消息头中的长度接收消息体
        data = sock.recv(message['packetSize'],socket.MSG_WAITALL)
        # print(data);
        data = np.frombuffer(data,dtype=np.uint8)
        print("data:",data);
        return message, data

    def _parseHeader(self,head):
        # parsing head 
        #颠倒矩阵顺序
        code = np.flip(head[4:6]).copy().view(dtype=np.uint16)
        request = np.flip(head[6:8]).copy().view(np.uint16)
        startSample = np.flip(head[8:12]).copy().view(np.uint32)
        packetSize = np.flip(head[12:16]).copy().view(np.uint32)

        message = {
            'code':code,
            'request':request,
            'startSample':startSample[0],
            'packetSize':packetSize[0]
        }

        return message

    def requestInfo(self):
        self.openflag=True
        # 获得设置信息
        # 请求获得基本信号：通道数目，采样率和数据包大小
        while self.openflag:
            sendBasicInfo = NeuroScanMessage().getBasicInfo()
            #发送header信息
            self.sock.send(sendBasicInfo)
            #接收消息（包括消息头和消息体）
            time.sleep(1)
            message,data = self.clientProcess(self.sock)
            # print(message,data)

            size = np.uint8(data[0:4]).copy().view(dtype=np.uint32)
            eegChan = np.uint8(data[4:8]).copy().view(np.uint32)
            sampleRate = np.uint8(data[8:12]).copy().view(np.uint32)
            datasize = np.uint8(data[12:16]).copy().view(np.uint32)
            # print("requestINFO22",size,eegChan,sampleRate,datasize)
            if(eegChan>100000):
                continue
            elif(len(eegChan)==0 and len(datasize)==0):
                eegChan=1
                size=24
                sampleRate=1000
                datasize=[4]
            else:
                self.openflag=False


            # print("requestINFO",size,eegChan,sampleRate,datasize)
            #从消息体中获取Info
            info = {
                'size':size,
                'eegChan':int(eegChan),
                'sampleRate':sampleRate,
                'datasize':datasize[0]
            }

            self.info = info
            return self

    def _unpackEEG(self,data):

    
        if self.info['datasize'] == 2:
            data = data.view(np.int16)
        elif self.info['datasize'] == 4:
            # print(len(packect))
            packect = data.view(np.single)
        print(len(packect))
        numSamples = int(len(packect)/self.info['eegChan'])
        packect = np.reshape(packect,(self.info['eegChan'],numSamples),order='F')
        packect = np.flipud(packect)
        
        # remove baseline
        packect = packect - np.repeat(np.median(packect,axis=-1,keepdims=True),numSamples,axis=1)

        return packect


    def requestChannelInfo(self):

        # 获得设置信息 
        offset_channelId    =                     1
        offset_chanLabel    = offset_channelId  + 4
        offset_chanType     = offset_chanLabel  + 80
        offset_deviceType   = offset_chanType   + 4
        offset_eegGroup     = offset_deviceType + 4
        offset_posX         = offset_eegGroup   + 4
        offset_posY         = offset_posX       + 8
        offset_posZ         = offset_posY       + 8
        offset_posStatus    = offset_posZ       + 8
        offset_bipolarRef   = offset_posStatus  + 4
        offset_addScale     = offset_bipolarRef + 4
        offset_isDropDown   = offset_addScale   + 4
        offset_isNoFilter   = offset_isDropDown + 4


        # Raw length
        chanInfoLen = (offset_isNoFilter + 4) - 1 
        # Length of CURRY channel info struct in bytes, consider padding
        chanInfoLen = round(chanInfoLen/8)*8

        channelNUM = self.info['eegChan']

        sendChannelInfo = NeuroScanMessage().getChannelInfo()

        # print(111111110+channelNUM)
        #发送header信息
        self.sock.send(sendChannelInfo)

        message,data = self.clientProcess(self.sock)

        #从data中获取label
        channelLabels = []
        for i in range(channelNUM):
            j = chanInfoLen*i
            # print(j)
            label = data[j+offset_chanLabel-1:j+(offset_chanType-1)]
            # print(label);
            label = label[:6].tolist()
            # print(label);
            label = ''.join([chr(item) for item in label ])
            # print(label);
            label = label.replace('\x00','')
            # print(label);
            channelLabels.append(label)
            # print(channelLabels);
        self.info['channels'] = channelLabels

        return self

    
    def downSample(self, data):

        trigger = data[-1:, :]
        trigger_num = len(trigger[trigger != 0])

        if trigger_num == 0:
            down_sample_data = data[:, ::4]  # 降采样至1/4
            return down_sample_data
        down_sample_data = data[:, ::4]  # 降采样至1/4
        trigger_index = np.where(trigger != 0)[1]
        # down_sample_trigger_index = []
        for i in trigger_index:
            down_sample_trigger_index = int(i / 4)
            down_sample_data[-1, down_sample_trigger_index] = trigger[0, i]

        return down_sample_data

    def get_time_stamp(self):
        ct = time.time()
        local_time = time.localtime(ct)
        data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        data_secs = (ct - int(ct)) * 1000
        time_stamp = "%s.%03d" % (data_head, data_secs)
        return time_stamp
