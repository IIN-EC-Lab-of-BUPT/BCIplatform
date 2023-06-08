#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
@Time : 2021/5/31 15:00
@Author : Nieeka
@Version：V 1.0
@File : NeuroScanEEGInterface.py
@Desciption :
"""
from abc import ABCMeta, abstractmethod


class NeuroScanEEGInterface(metaclass=ABCMeta):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def read_thread(self):
        pass


    @abstractmethod
    def downSample(self, data):
        pass
