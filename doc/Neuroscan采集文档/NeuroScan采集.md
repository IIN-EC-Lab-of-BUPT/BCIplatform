# NeuroScan采集

本系统用于NeuroScan原始数据的处理和转发，使用socket与脑电数据发送端通信，再使用kafka将处理后的数据转发给处理端。

### 采集入口：

```python
if __name__ == '__main__':
    collect = Collect(Device_confPath)
    collect.run(confPath,initialPath)
```

### kafka配置文件：

路径

```python
confPath = r"./MessageQueue/usage/config/producer-config.json" 
```

配置内容：主机加端口

```python
{"bootstrap.servers": "server:60000","linger.ms": "1"}
```

### NeuroScan配置文件：

路径

```python
Device_confPath = r"./DeviceModule/config/NeuroScanEEG.json"
```

配置内容

```python
{
  "device_name": "NeuroScan",
  "hostname": "localhost",
  "port": 4455,
  "n_chan": 10,
  "topic":"NeuroScanEEG",
  "log_level":2
}
```

*其中device_name为设备名称，hostname为主机IP，port为socket通信端口，应该和采集设备端口保持一致，n_chan为采集端输入的导数，topic为kafka通信的话题,log_level为日志级别*



### 建立采集数据处理转发线程（调用Collect时创建）：

```python
"""
参数说明：
线程名threadName（自定义, string）
设备名device（自定义, string）
导联数n_chan（不包括Trigger,int）
运行放大器驱动软件的终端的IP地址hostname(string)
放大器驱动软件用于发送数据的tcp端口号port(int)
发送至kafka的topic名称(string)
"""
thread_data_server = NeuroScanEEGThread(threadName='NeuroScanEEG', device=target_device['device_name'],n_chan=target_device['n_chan'],
hostname=target_device['hostname'], port=target_device['port'],
topic=target_device['topic']) 
```


### 与数据池建立kafka连接（调用Collect.run时进行连接）：

```python
self.thread_data_server.connect_kafka(confPath,initialPath)
```



### 与采集设备建立socket连接（调用Collect.run时进行连接）：

```python
notconnect = thread_data_server.connect()
if notconnect:
    thread_data_server.logger.debug("Can't connect recorder")
    raise TypeError("Can't connect recorder, Please open the hostport ")
else:
    thread_data_server.start()
```

*使用socket与采集设备通信，连接不成功时继续重连，直到连接成功或者尝试次数超过19*

*kafka和socket连接成功后，start采集线程*


### 数据处理流程:

```python
def read_thread(self):   
    """
    visit eegthread, catch sockets and parse sockets, append parsed data to ringbuffer
    """
    self.requestInfo()
    self.requestChannelInfo()
    self.receiveThread=threading.Thread(target=self.parseData)
    self.sendThread=threading.Thread(target=self.sendData)
    self.receiveThread.start()
    self.sendThread.start()
```
在线程中先完成基础信息的获取，之后分别开启两个线程，完成数据采集和数据转发的功能。

### requestInfo函数：

```python
def requestInfo(self):
    """
    通过与采集设备socket通信获得基本信号，即通道数目，采样率和数据包大小
    """
```

### requestChannelInfo函数：

```python
def requestChannelInfo(self):
    """
    通过与采集设备socket通信请求导联信息
    """
```

### parseData函数：

```python
def parseData(self):
    """
    handle data,message and event
    """
```

*作为线程，持续从采集端接收消息和数据，根据消息头部的信息得知发来的数据类型，对不同类型做出相应处理。如果根据消息头部的信息得知发来的是数据信息，对数据进行解析和打包操作。如果根据消息头部的信息得知发来的是阻抗信息，暂停接收数据只接收阻抗，接收完毕后继续接收数据。做完降采样的操作之后将处理好的数据放入先入先出队列queue之中。*

### 可能异常：

```python
socketException
```

```python
self.info["eegChan"] != self.n_chan
```

*如果socket通信中断，在except中调用connect()继续连接，连接完成后可继续收发数据不受中断影响；如果发来的导数与NeuroScan中预设的导数不同，直接断开socket连接。*

### sendData函数：

```python
def sendData(self):
    """
    send bytestream data to kafka
    """
```

*当队列queue中有数据的时候，从中获取到数据并转化为字节流发送到kafka服务器*

