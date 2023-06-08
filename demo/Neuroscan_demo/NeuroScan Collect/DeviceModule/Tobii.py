import json
import queue
import socket
import threading
import time
import numpy as np
from struct import *
from DeviceModule.tobiiUtils import *
from EEGPlatformCommunicationModule4py.communicationModuleImplement.CommunicationInitial import CommunicationInitial
from EEGPlatformCommunicationModule4py.communicationModuleImplement.CommunicationProducer import CommunicationProducer


class Tobii:
    def __init__(self, conf):
        self.sensor_queue = queue.Queue()
        self.exist_gidx = []
        self.gaze_list = []
        self.producer = None
        self.PORT = 49152
        self.GLASSES_IP = None
        self.peer = None
        self.MULTICAST_ADDR = 'ff02::1'
        self.KA_DATA_MSG = b"{\"type\": \"live.data.unicast\", \"key\": \"some_GUID\", \"op\": \"start\"}"
        self.sendThread = threading.Thread(target=self.send_sensor)
        self.sendThread2 = threading.Thread(target=self.send_gaze)
        with open(conf, 'r') as load_f:
            config = json.load(fp=load_f)
            self.topic = config["topic"]

    # 发现Tobii设备
    def connect(self):
        try:
            self.discovery()
            self.peer = (self.GLASSES_IP, self.PORT)
            self.mksock(self.peer)
            return False
        except Exception as e:
            print("错误类型为", e)
            return True

    # 开始与Tobii通信
    def start(self):
        project_id, project_time = self.create_project()
        project_eagleId = self.update_project(project_id, project_time)
        participant_id = self.create_participant(project_id)
        participant_eagleId = self.update_participant(project_id, participant_id)
        recording_id = self.create_recording(participant_id)
        recording_eagleId = self.update_recording(recording_id, participant_id, project_id)
        calibration_id = self.create_calibration(participant_id)
        self.start_calibration(calibration_id)
        try:
            calibration_state = self.CalibrationState(calibration_id, 'ca_state', ['failed', 'calibrated'])
        except Exception as e:
            print("错误类型为", e)

        if calibration_state == "calibrated":
            print("calibration is finished")
            data_socket = self.mksock(self.peer)
            data_socket.bind(('', 5543))
            td = threading.Timer(0, self.send_keepalive_msg, [data_socket, self.KA_DATA_MSG, self.peer])
            td.start()
            # self.connect_kafka()
            self.sendThread.start()
            self.sendThread2.start()
            self.receive_msg(data_socket)
        if calibration_state == "failed":
            print("calibration is failed,pleast try again!")
            data_socket = self.mksock(self.peer)
            data_socket.bind(('', 5543))
            td = threading.Timer(0, self.send_keepalive_msg, [data_socket, self.KA_DATA_MSG, self.peer])
            td.start()
            # self.connect_kafka()
            self.sendThread.start()
            self.sendThread2.start()
            self.receive_msg(data_socket)
        else:
            print("获取校准信息时出现错误，请重新校准")

    def discovery(self):
        s6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s6.bind(('::', 13007))
        s6.sendto((b'{"type":"discover"}'), (self.MULTICAST_ADDR, 13006))
        while True:
            data, address = s6.recvfrom(1024)
            if data != None:
                json_data = json.loads(data)
                print(json_data)
                self.GLASSES_IP = json_data["ipv4"]
                break

    # 创建项目
    def create_project(self):
        response = post_project1('/api/projects', self.GLASSES_IP)
        print(response)
        return response['pr_id'], response['pr_created']

    # 更新项目信息
    def update_project(self,id, time):
        response, eagleId = post_project2('/api/projects/', self.GLASSES_IP, id, time)
        print(response)
        return eagleId

    # 创建被试
    def create_participant(self,pid):
        response = post_participant1('/api/participants', self.GLASSES_IP, pid)
        print(response)
        return response['pa_id']

    # 更新被试信息
    def update_participant(self,project_id, participant_id):
        response, eagleId = post_participant2('/api/participants', self.GLASSES_IP, project_id, participant_id)
        print(response)
        return eagleId

    # 创建记录
    def create_recording(self,paid):
        response = post_recording1('/api/recordings', self.GLASSES_IP, paid)
        print(response)
        return response['rec_id']

    # 更新记录
    def update_recording(self,rid, paid, pid):
        response, eagleId = post_recording2('/api/recordings', self.GLASSES_IP, rid, paid, pid)
        print(response)
        return eagleId

    # 创建校准
    def create_calibration(self,participant_id):
        response = post_calibration1('/api/calibrations', self.GLASSES_IP, participant_id)
        print(response)
        return response['ca_id']

    # 开始校准
    def start_calibration(self,cid):
        response = post_calibration2('/api/calibrations', self.GLASSES_IP, cid)
        print(response)

    # 获取校准信息
    def CalibrationState(self,cid, key, value):
        ca_flag = True
        while ca_flag:
            response = get_calibration_state('/api/calibrations', self.GLASSES_IP, cid)
            if response[key] in value:
                ca_flag = False
                print(response[key])
                return response[key]
            else:
                time.sleep(1)

    # Create UDP socket
    def mksock(self,peer):
        iptype = socket.AF_INET
        if ':' in peer[0]:
            iptype = socket.AF_INET6
        return socket.socket(iptype, socket.SOCK_DGRAM)

    # 发送keep-alive消息
    def send_keepalive_msg(self,socket, msg, peer):
        while True:
            socket.sendto(msg, peer)
            time.sleep(1)

    # 连接kafka
    def connect_kafka(self, initialPath, confPath):
        connecet_kafka = False
        while not connecet_kafka:
            try:
                CommunicationInitial.topicCreate(self.topic, initialPath)
                self.producer = CommunicationProducer(confPath)
                connecet_kafka = True
            except:
                print("连接到kafka时出现异常")

    # 接收眼动信号
    def receive_msg(self,socket):
        while True:
            template_json = {"ts": {"index": 0, "left": {"gd": {"range": [0.0, 0.0, 0.0], "s": 0},
                                                         "pc": {"range": [0.0, 0.0, 0.0], "s": 0},
                                                         "pd": {"range": 0.0, "s": 0}},
                                    "right": {"gd": {"range": [0.0, 0.0, 0.0], "s": 0},
                                              "pc": {"range": [0.0, 0.0, 0.0], "s": 0}, "pd": {"range": 0.0, "s": 0}},
                                    "l": {
                                        "value": 0, "gp": [0.0, 0.0]}, "gp3": [0.0, 0.0, 0.0]}}
            data = socket.recv(1024)
            data = data.decode(encoding="utf-8")
            json_data = json.loads(data)
            # print(json_data)
            if "gidx" not in json_data:
                self.sensor_queue.put(data)
            else:
                index = json_data["gidx"]
                if index in self.exist_gidx:
                    print("这是一个已有的index")
                    if self.gaze_list[-1]["ts"]["index"] == index:
                        newdict = self.add_gaze(self.gaze_list[-1], json_data)
                    else:
                        print("出现包延迟到达的状况")
                        if len(self.gaze_list)>3:
                            if self.gaze_list[-2]["ts"]["index"] == index:
                                newdict = self.add_gaze(self.gaze_list[-2], json_data)
                            if self.gaze_list[-3]["ts"]["index"] == index:
                                newdict = self.add_gaze(self.gaze_list[-3], json_data)
                            else:
                                index_flag = True
                                for d in self.gaze_list:
                                    if d["ts"]["index"] == index:
                                        newdict = self.add_gaze(d,json_data)
                                        index_flag = False
                                        break
                                if index_flag:
                                    print("========================")
                                    print("ERROR:gidx not found")
                    print(newdict)
                else:
                    print("这是一个新的index")
                    self.exist_gidx.append(index)
                    raw = template_json
                    raw["ts"]["index"] = index
                    newindex = self.add_gaze(raw,json_data)
                    print(newindex)
                    self.gaze_list.append(newindex)

    # 添加眼动数据
    def add_gaze(self,dict,json_data):
        if "eye" in json_data:
            if json_data["eye"]=="left":
                if "gd" in json_data:
                    dict["ts"]["left"]["gd"]["range"] = json_data["gd"]
                    dict["ts"]["left"]["gd"]["s"] = json_data["s"]
                if "pc" in json_data:
                    dict["ts"]["left"]["pc"]["range"] = json_data["pc"]
                    dict["ts"]["left"]["pc"]["s"] = json_data["s"]
                if "pd" in json_data:
                    dict["ts"]["left"]["pd"]["range"] = json_data["pd"]
                    dict["ts"]["left"]["pd"]["s"] = json_data["s"]
            else:
                if "gd" in json_data:
                    dict["ts"]["right"]["gd"]["range"] = json_data["gd"]
                    dict["ts"]["right"]["gd"]["s"] = json_data["s"]
                if "pc" in json_data:
                    dict["ts"]["right"]["pc"]["range"] = json_data["pc"]
                    dict["ts"]["right"]["pc"]["s"] = json_data["s"]
                if "pd" in json_data:
                    dict["ts"]["right"]["pd"]["range"] = json_data["pd"]
                    dict["ts"]["right"]["pd"]["s"] = json_data["s"]
        if "l" in json_data:
            dict["ts"]["l"]["value"] = json_data["l"]
            dict["ts"]["l"]["gp"] = json_data["gp"]
        if "gp3" in json_data:
            dict["ts"]["gp3"] = json_data["gp3"]
        return dict

    # 发送sensor至Kafka
    def send_sensor(self):
        while True:
            if self.sensor_queue.qsize() > 0:
                try:
                    packet = self.sensor_queue.get().encode()
                    int_max = np.iinfo(np.uint32).max
                    head1 = pack("I", int_max)
                    head2 = (2).to_bytes(1, byteorder='little')
                    head3 = (1).to_bytes(1, byteorder='little')
                    head4 = (0).to_bytes(1, byteorder='little')
                    head5 = (1).to_bytes(2, byteorder='little')
                    head6 = (0).to_bytes(4, byteorder='little')
                    wholepacket = head1 + head2 + head3 + head4 + head5 + head6 + packet
                    self.producer.send(self.topic, wholepacket)
                except Exception as e:
                    print("错误类型为", e)
    # 发送gaze至Kafka
    def send_gaze(self):
        while True:
            if len(self.gaze_list)>10:
                try:
                    packet = self.gaze_list.pop(0)
                    packet = json.dumps(packet).encode()
                    int_max = np.iinfo(np.uint32).max
                    head1 = pack("I", int_max)
                    head2 = (2).to_bytes(1, byteorder='little')
                    head3 = (1).to_bytes(1, byteorder='little')
                    head4 = (0).to_bytes(1, byteorder='little')
                    head5 = (0).to_bytes(2, byteorder='little')
                    head6 = (0).to_bytes(4, byteorder='little')
                    wholepacket = head1 + head2 + head3 + head4 + head5 + head6 + packet
                    self.producer.send(self.topic, wholepacket)
                except Exception as e:
                    print("错误类型为", e)
