# 说明

MQTT 边缘网关摄像头管理模块的注册和上报相关消息接口实现。

## 环境说明

Python版本为3.6.6
需要额外安装的包： paho-mqtt==1.4.0

## 项目结构说明

```
- mqtt_edge
  - config  配置
    - config.py 配置服务Host, Port, 数据库地址等等
  - logger 日志配置
    - __init__.py  日志配置
	- log.txt  日志文件
  - reports  边缘 mqtt client 上报的消息接口
    - __init__.py  
    - report_ai_event.py
    - report_alarm.py
	- report_config.py  
  - tests  本地开发的一些测试支持
    - cloud_client.py  模拟云端的实现逻辑
	- create_test_table.py  创建测试用的数据库
  - utils  一些工具函数
    - dadta_utils.py  对数据进行处理的工具函数
	- sql_utils.py  对sqlite执行的封装工具
  - test_cloud.py  模拟云端运行入口，在没有cloud提供服务时，可以需要在当前目录下执行 python cloud.py 来模拟提供服务。
  - edge_client.py  边缘 mqtt client 的实现逻辑
  - main.py  启动 client 的入口，执行 python main.py 启动服务
  - mqtt_base.py mqtt client 的父类
  - sqlite.db  测试数据库
- docker-compose.yml
- Dockerfile
- requirements.txt
```

## 运行

### 1 如果没有cloud，可以执行以下命令模拟云端

```
cd mqtt_edge
python test_cloud.py
```

服务会进入loop状态中，终端会打印相关信息。

### 2 注册消息

```
cd mqtt_edge
python main.py

```

服务会进入loop状态中，终端会打印相关信息。
服务首先会进行注册，注意cloud 和终端的打印信息。

### 3 上报事件

上报事件可以在python解释器中模拟：

```
>>> from reports.report_ai_event import run as run_ai_event
>>> run_ai_event()
```
注意cloud和终端的打印信息


