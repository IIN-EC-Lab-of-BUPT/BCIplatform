#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
@Time : 2020/12/14 14:23
@Author : Nieeka
@Version：V 1.0
@File : ReceiverOperationMain.py
@Desciption :启动脚本
"""
import json
import sys
from DeviceModule.NeuroScanEEG import NeuroScanEEGThread
from DeviceModule.Tobii import Tobii


class Collect:
    def __init__(self,Device_confPath):

        with open(Device_confPath, 'r') as load_f:
            target_device = json.load(fp=load_f)

        """
        参数说明：
        线程名（自定义, string）
        设备名（自定义, string）
        道导联数（不包括Trigger,int）
        运行放大器驱动软件的终端的IP地址(string)
        放大器驱动软件用于发送数据的tcp端口号(int)
        发送至kafka的topic名称(string)
        """
        if target_device["device_name"] == "NeuroScan":
            self.thread_data_server = NeuroScanEEGThread(threadName='NeuroScanEEG', device=target_device['device_name'],
                                                   n_chan=target_device['n_chan'],
                                                   hostname=target_device['hostname'], port=target_device['port'],
                                                   topic=target_device['topic'],loglevel=target_device['log_level'])  # 建立线程
        elif target_device["device_name"] == "TobiiScan":
            self.thread_data_server = Tobii(Device_confPath)
        else:
            sys.exit(0)
        self.thread_data_server.Daemon = True

    def run(self,confPath,initialPath):
        #连接kafka和socket
        self.thread_data_server.connect_kafka(confPath,initialPath)
        notconnect = self.thread_data_server.connect()

        if notconnect:
            if self.thread_data_server.level!=0:
                self.thread_data_server.logger.debug("Can't connect recorder, Please open the hostport ")
            raise TypeError("Can't connect recorder, Please open the hostport ")
        else:
            self.thread_data_server.start()

