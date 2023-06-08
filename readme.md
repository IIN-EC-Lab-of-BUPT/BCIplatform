# BCIPlatform

BCIPlatform是一个开源的分布式平台，致力于帮助开发脑机接口领域的软件。

## BackGround
该平台是基于消息通信的脑机接口系统，可支持分布式部署，解决了现有脑机接口系统单机应用和计算能力容易受单机性能限制的问题。该平台由通信平台、数据采集子系统和通用持久性子系统组成。通过对上述模块的灵活组合或切割，用户可以构建单机轻量级脑机接口系统或多人实时脑机接口系统的分布式部署，甚至构建脑机接口云平台。
## Features

脑机接口系统支撑平台的设计过程采用了基于分布式组件的设计思想，基于主题的多平台兼容的设计理念。在未来，我们将使用远程过程调用技术来解决多语言兼容问题。
分布式组件化设计思想是指平台提供商将可用的支持服务根据其功能划分为不同的组件，这些组件是低耦合的，支持在不同的物理机上分布式部署，平台用户可以根据需要对组件进行组合和切割，以满足系统的功能需求。基于分布式组件的平台组件设计使系统具有更高的可扩展性和部署灵活性。
为了支持分布式部署系统中组件之间的跨计算机交互，简化通信过程，该平台采用消息中间件作为组件间通信的解决方案。在通过消息中间件进行通信的过程中，消息发送方和消息接收方都将主题作为消息发送或接收的目的地，在逻辑层面上，主题可以看作是消息数据的集合。目前基于主题的通信方式兼容Windows、Linux、MacOS等主流计算机操作系统，使得支持平台具有多平台兼容性。



## Kafka usage


### 安装步骤：
1.在命令行中转到安装包“setup.py“文件所在路径下\
2.激活待安装的虚拟环境\
3.支持以下两种安装方式：

#### 安装方式1

完成步骤2后执行如下代码：
```
python setup.py install
```
使用该方式安装完成后可删除原始文件。

#### 安装方式2(非该平台开发人员请谨慎使用)

完成步骤2后执行如下代码：
```
python setup.py develop
```
使用该方式安装时，下载本模块安装包并解压后，请妥善放置其解压文件，安装完成后再次移动、改动或删除其解压文件将导致该模块无法正常使用。

---

另：本模块依赖于第三方类库confluent-kafka，该类库推荐python3版本3.8及以下。如果在3.8及以上版本中安装失败，并提示`ImportError: DLL load failed while importing cimpl: with confluent Kafka python using windows`，可通过[该链接](https://github.com/confluentinc/confluent-kafka-python/issues/1221)中给出的方法解决，解决失败请回退至python3.6版本。


如果安装命令执行完毕后提示confluent-kafka安装失败，请尝试运行以下代码后重试：

```
pip install confluent-kafka
```

---
---
### 使用说明

*接口实现位于communicationModuleImplement包,配置示例位于communicationModuleUsage/config包*

*使用者只需关注生产者类、消费者类及topic操作中的“创建topic”方法*

### topic操作：

```python
class CommunicationInitial(CommunicationInitialInterface)
```

#### 查询topic列表

```python
def topic_query(communication_character: QueryInterface) -> list:
```

```python
:param communication_character: a instance of interface "QueryInterface"
:return: a list of all topic names, type: list<str>
:throw: TopicQueryFailed, when failed "retry_limit" times
```

#### 可能异常：

```python
TopicQueryFailed # 通常由于网络问题导致，发生后建议检查同Kafka服务器的网络联通性，或联系管理员检查Kafka服务健康度
```

#### 创建topic

```python
def topic_create(topic: str, conf_path: str, num_partitions=1, replication_factor=1):
```

```python
:param topic: the name of the topic that you want to create
:param conf_path: path of configuration file, "bootstrap.servers" must be set
:param num_partitions: the partition number of the topic that you want to create, default: 1
:param replication_factor: the replication number of the topic that you want to create, default: 1
:return: name of the topic which is created by this method, type: str
:throw: TopicCreateFailed, when failed
				NoConfigFileException, when there is no config file in your config path
				WrongConfigContextException, when an invalid key is written in the configuration file
```

#### 可能异常：

```python
NoConfigFileException # 配置文件不存在
WrongConfigContextException #　配置文件内容有误
TopicCreateFailed # topic创建失败，发生后建议检查同Kafka服务器的网络联通性，或联系管理员检查Kafka服务健康度
```

#### 删除topic

```python
def topic_delete(topic: str, conf_path: str):
```

```python
:param topic: the name of the topic that you want to create. type: str
:param conf_path: path of configuration file, "bootstrap.servers" must be set
:return: name of the topic which is deleted by this method, type: str
:throw: TopicDeleteFailed, when failed or there is no topic to delete
				NoConfigFileException, when there is no config file in your config path
				WrongConfigContextException, when an invalid key is written in the configuration file
```

#### 可能异常:

```python
NoConfigFileException # 配置文件不存在
WrongConfigContextException #　配置文件内容有误
TopicCreateFailed # topic删除失败
```

### 生产者：

```python
class CommunicationProducer(CommunicationProducerInterface, QueryInterface)
```

*调用者只需要关注__init__、__send__和__close__的用法*

#### 初始化

```python
def __init__(self, conf_path: str):
```

```python
:param conf_path: the path of the producer config file that you want to use
:throw: NoConfigFileException, when there is no config file in your config path
```

#### 发送消息

```python
def send(self, topic: str, value: bytes, timeout: float = 1, key=None) -> None:
```

```python
:param topic: the topic name that you want to send message to, type: str
:param value: the message context, type: bytes
:param timeout: the timeout for sending a msg, but that doesn't mean the msg sending is failed
:param key: see "key" concept in kafka docs
:throw: WrongMessageValueType, when "value" param isn't bytes-type
```

##### 可能异常：

```python
WrongMessageValueType #　消息类型非bytes
```

#### 关闭

```python
def close(self, timeout: float = 1) -> None:
```

```
release resources
:param: timeout: the flush timeout before closed
```

#### 关闭动作：

推送生产者队列中的全部消息

### 消费者：

```python
class CommunicationConsumer(CommunicationConsumerInterface, QueryInterface)
```

*调用者只需要关注__init__、__receive__、__timeStampReceive__和__stop__的用法*

####初始化

```python
def __init__(self, conf_path: str, consumer_id: str):
```

```python
:param conf_path: the path of the producer config file that you want to use
:param consumer_id: should be unique in the system, UUID suggested
:throw: NoConfigFileException, when there is no config file in your config path
```

#### 订阅

```python
def subscribe(self, topic: str) -> None:
```

```python
:param topic: the name of the topic this consumer need to subscribe
:throw: TopicNotAvailableException, when subscribing a topic that doesn't exist
```

#####可能异常：

```python
TopicNotAvailableException #　topic不存在或其他原因订阅失败，发生后建议手动创建topic，或检查同Kafka服务器的网络联通性，或联系管理员检查Kafka服务健康度
```

#### 取消订阅

```python
def unsubscribe(self) -> None:
```

#### 接收消息

```python
def receive(self) -> bytes:
```

```python
:return: message received within 0.1s. type: bytes (when the message is received) or None (when there is no message in 0.1s)
:throw: NoSubscribeException, when calling this method before subscribe a topic
```

#### 接收带有时间戳的消息

```python
def timestamp_receive(self) -> list:
```

```python
:return: a list of timestamp and message value.
the first element in the list is a tulpe of timestamp. the first element is timestamp type,
which is a number in 0, 1 or 2.
0 means the timestamp isn't available, in this case, the return timestamp should be ignore.
1 means the return timestamp is the number of milliseconds of the message creation time.
2 means the return timestamp is the number of milliseconds of the broker receive time.
the first element in the list is bytes of  message value.
type: [(int, int), bytes] or None(when there is no message in timeout)
:throw: NoSubscribeException, when calling this method before subscribe a topic
```

#### 关闭

```python
def close(self) -> None:
```

##### 关闭动作：

取消订阅、关闭消费者

### 配置文件说明

#### CommunicationInitial类的配置文件

配置文件路径：./communicationModuleUsage/config/initial-config.json

##### 话题管理配置文件示例

`{`

`“bootstrap.servers”: “server:60000”,`
 `"retry.limit": “3”`

`}`

##### 字段含义：

- **bootstrap.servers**：type：string。（下同）通信服务器地址，如Kafka服务部署方式或服务器IP有变，请询问管理员具体地址及使用方式。（在默认部署方式下，需在计算机中添加“<host名>   <IP地址>”映射，然后在此处填入host名和端口号。host名（或IP）与端口号之间以英文冒号分隔。）
- **retry.limit**：  type：string，内容需为大于等于0的int型数字。 `CommunicationInitial.topic_create`方法重试次数。如果网络环境较差，建议将该字段设为较大值，但如果该字段值过大，将导致用户无法及时发现网络异常。

#### CommunicationProducer类的配置文件

配置文件路径：./communicationModuleUsage/config/producer-config.json

##### 生产者配置文件示例

`{`

`"bootstrap.servers": "server:60000",`

`"debug.log.enable": "false",`

`"linger.ms": "0",`

`"retry.limit": "0",` 

`"realtime.flush": "true”`

`}`

##### 字段含义：

- **debug.log.enable**： type：string，enum：{false，true}，大小写不敏感。（下同）是否开启生产者/消费者debug级别的日志记录，如果开启，则生产者/消费者将在每次生产/消费动作完成后记录一条debug级别的日志，在大量、低间隔进行生产/消费活动时建议关闭该日志。
- **linger.ms**：type：string，内容需为int型数字。对生产者发送速度有较高要求时建议将该字段设为较小值。
- **retry.limit**： type：string，内容需为大于等于0的int型数字。 `CommunicationProducer.list_topics`方法重试次数。如果网络环境较差，建议将该字段设为较大值，但如果该字段值过大，将导致用户无法及时发现网络异常。
- **realtime.flush**： type：string，enum：{false，true}，大小写不敏感。是否开启实时推送。如果开启该功能可以保证消息尽快发出，但开启后会导致`CommunicationProducer.send`方法在被调用后产生大致10ms的阻塞。

#### CommunicationConsumer类的配置文件

配置文件路径：./communicationModuleUsage/config/consumer-config.json



##### 消费者配置文件示例

`{` 

`"bootstrap.servers": "server:60000",`

`"auto.offset.reset": "latest",`

`"enable.auto.commit": "False",`

`"retry.limit": "3",` 

`"debug.log.enable": "False”`

`}`

##### 字段含义：

- **auto.offset.reset**： type：string，enum：{latest，earliest，none}，大小写敏感。消费者从消息队列的何处开始消费。该参数不建议改动，默认给出的设置将使消费者从其启动时的最新消息开始消费。
- **enable.auto.commit** ：该参数不建议改动。
- **retry.limit**： type：string，内容需为大于等于0的int型数字。 `CommunicationConsumer.list_topics`方法重试次数。如果网络环境较差，建议将该字段设为较大值，但如果该字段值过大，将导致用户无法及时发现网络异常。

If you would like to contribute code or feedback questions to NeuroStore, you can do so in the following ways:

* Submit Questions or Suggestions: If you experience any problems or have any suggestions while using NeuroStore, please submit an Issue. We'll get back to you as soon as possible.
* Submit code: If you would like to submit code for NeuroStore, Fork the project first, then make changes in your own repository, and submit a Pull Request to us. We will review your code and merge it as soon as possible.
* Contact us: If you would like to contact us, please email JelenaBeatrice387@outlook.com
##Trigger Usage
本模块基于python3.8版本

Neuracle的接口实现位于Neuracle包中，Neuroscan的接口实现位于Neuroscan包中

Neuracle支持串口或并口发送，Neuroscan只支持并口发送

使用者只需要参考Trigger接口说明调用TriggerController.py文件即可

Trigger测试程序位于TriggerTest.py文件中

注意：由于并口每次发送trigger后需要重新将引脚电平置为低电平，所以使用并口发送trigger的间隔请大于20ms

### 前期准备

#### 检查是否可正确识别串口/并口

右键我的电脑—管理—设备管理器，检查串口/并口是否可以正确识别，如果未正确识别则应安装相应驱动。串口驱动在安装Neuracle软件时安装，并口驱动请按照并口卡的型号搜索其相应驱动。正确识别串口/并口后请记录其端口号。如：串口为COM3；并口端口号查看：右键并口—属性—资源—I/O范围，将首位16进制数换算为10进制，如：3FF8换算为16376.

#### 安装inpoutx64驱动

使用并口发送trigger前需要安装inpoutx64对应的驱动，驱动位于TriggerDependency—1—Win32下，双击InstallDriver.exe即可安装驱动。

### 配置串口/并口

##### USB Trigger配置

a.关闭USB选择性暂停
设置 - 电源和睡眠 - 其他电源设置 - 选择电源计划 - 选择“高性能模式”- 更改计划设置 - 更改高级电源设置 - 找到“USB设置”- USB选择性暂停设置： 设置为“已禁用”(系统默认为"已启用"）
b.USB 端口延迟设置
我的电脑-右键-属性-左侧边栏"设备管理器" - 与TriggerBox 连接的USB接口（安装TriggerBox驱动后，通常位于 端口(COM和LPT)-USB Serial Port(COM X) 位置) - 右键”属性“-端口设置-高级
BM选项中 延迟计时器(毫秒) - 修改设置为'1'(Windows 10 系统安装驱动后默认设置为16ms)

##### 通过PCI-Express 转并口 发送Trigger 配置

关闭PCI-Express并口 链接状态电源管理
设置 - 电源和睡眠 - 其他电源设置 - 选择电源计划 - 选择“高性能模式”- 更改计划设置 - 更改高级电源设置 - 找到“PCI Express”-链接状态电源管理： 设置为“关闭”(系统默认即为"关闭"）

##### 485接口接收Trigger配置

我的电脑-空白处点右键-属性-设备管理器-端口(COM和LPT)-确定485接口转USB连接线所对应的COM口-右键属性-端口设置-高级-修改对应COM端口号为COM12

### Trigger接口说明

#### 实例化TriggerController

```python
trigger = TriggerController(eegServerType, triggerHandle, port)
```

```python
:param eegServerType: 输入'neuracle'则使用neuracle的trigger系统,输入'neuroscan'则使用neuroscan的trigger系统
:param triggerHandle: 输入'serial'表示使用串口,输入'parallel'表示使用并口
:param port: 串口/并口所对应的端口,如:neuracle串口输入'COM3'(字符串格式),neuracle/neuroscan并口输入32760;
```

#### 打开端口

```python
trigger.open()
```

#### 发送Trigger事件

```python
trigger.send(event)
```

```python
:param event: 输入想输入的trigger值,取值范围为1-255之间的整数
```

### 关闭

```python
trigger.close()
```


## License

Distributed under the GNU General Public License v2.0 License. See `LICENSE` for more information.

## Contact

Email: JelenaBeatrice387@outlook.com

## Acknowledgements
- [kafka](https://github.com/apache/kafka)
- [kafka-python](https://github.com/dpkp/kafka-python)
- [MySQL](https://github.com/mysqljs/mysql)
- [BIDS](https://bids.neuroimaging.io/)
- [COBIDAS](https://www.humanbrainmapping.org/cobidas)
# BCIplatform
# BCIplatform
