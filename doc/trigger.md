# trigger模块使用说明

- 本模块基于**Python 3.8**版本

- trigger发送模块的具体实现位于impl包中

- ParallelTriggerImpl是使用inpoutx64驱动发送并口trigger的实现方式

- **使用者只需要参考TriggerInterface中的接口说明调用TriggerController即可**

- Trigger用例程序位于TriggerUsage中

> 注意：由于并口每次发送trigger后需要重新将引脚电平置为低电平，所以不要连续调用send()，应保证一定的调用间隔，否则会出现异常

## 前期准备

### 1. 检查是否可正确识别端口

**右键此电脑—管理—设备管理器**，检查并口是否可以正确识别，如果未正确识别则应安装相应驱动。

并口驱动：请按照并口卡的型号搜索其相应驱动。

正确识别并口后请记录其端口号。 并口端口号查看：**右键并口（LPT1）—属性—资源—I/O范围**，记录7FF8即可

### 2. 安装inpoutx64驱动

使用并口发送trigger前需要安装inpoutx64对应的驱动，驱动位于**trigger—TriggerDependency—1—Win32**下，双击InstallDriver.exe即可安装驱动。

### 3. 配置并口

#### 通过PCI-Express 转并口 发送Trigger 配置

关闭PCI-Express并口 链接状态电源管理：设置 - 电源和睡眠 - 其他电源设置 - 选择电源计划 - 选择“高性能模式”- 更改计划设置 - 更改高级电源设置 - 找到“PCI Express”-链接状态电源管理： 设置为“关闭”(系统默认即为"关闭"）

#### 485接口接收Trigger配置
如果接收trigger时使用到了485线（如Neuracle的TriggerBox使用485线接收Trigger），则需要进行相应设置。我的电脑-右键-属性-左侧边栏"设备管理器" - 与TriggerBox 连接的USB接口（安装TriggerBox驱动后，通常位于 端口(COM和LPT)-USB Serial Port(COM X) 位置) - 右键”属性“-端口设置-高级
BM选项中 **延迟计时器(毫秒) - 修改设置为'1'**(Windows 10 系统安装驱动后默认设置为16ms)。之后**修改对应COM端口号为COM12**

## Trigger接口说明

### 实例化TriggerController

```python
trigger_ctrl = TriggerController(port: int)
"""
:param port: 并口所对应的端口，如:并口输入十进制32760或十六进制0x7FF8
"""
```

### 打开端口

```python
trigger_ctrl.open() -> bool
"""
开启端口的方法
:return: 成功返回True，失败返回False
"""
```

### 发送Trigger事件

```python
trigger_ctrl.send(event: int) -> bool
"""
发送trigger的方法
:param event: 发送的trigger值，trigger值应为1-255之间的整数
:return: 发送成功返回True，发送失败返回False
"""
```

### 关闭端口

```python
trigger_ctrl.close() -> bool
"""
关闭端口的方法
:return: 关闭成功返回True，关闭失败返回False
"""
```

## 其他使用注意事项

- 默认情况下，trigger控制器不是单例，如果需要可以将TriggerController中相应代码解除注释
- `open()` 方法保证了线程安全，但是原则上不应该多次调用
- `send()` 方法未做线程安全处理，以保证发送trigger的性能，不要多线程调用该方法
- `open() send() close()`  方法都设置了返回值，建议接收返回值并判断打开/发送/关闭操作是否成功，如果未成功，可以再次调用
- 由于并口每次发送trigger后需要重新将引脚电平置为低电平，所以不要连续调用send()，应保证一定的调用间隔，否则会出现异常
