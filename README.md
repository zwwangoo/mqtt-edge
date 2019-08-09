# 说明

MQTT 边缘网关摄像头管理模块的注册和上报相关消息接口实现。可以通过WEB界面模拟边缘设备和云端的通信过程。

## 环境说明

Python版本为3.6.6

```
pip install -r requirements.txt
```

## 项目结构说明

```
- mqtt_edge
  - clients mqtt client 类
    - __init__.py  mqtt clinet的父类
	- cloud_client.py  cloud client 类
	- edge_client.py  edge client 类
  - instance  配置
    - config.py flask web的一些配置，其中包括模拟云端的mysql连接配置。
  - logger 日志配置
    - __init__.py  日志配置
	- log.txt  日志文件
  - templates  静态网页
	- index.html
  - utils  一些工具函数
    - dadta_utils.py  对数据进行处理的工具函数
	- sql_utils.py  对sqlite执行的封装工具
  - app.py  flask的入口文件
  - cloud.py  cloud web接口
  - edge.py  edge web 接口
  - extensions.py  flask 使用的第三方库
  - sqlite.db  边缘设备的数据库
- scripts  本地开发的一些测试支持
  - create_test_table.py  创建测试用的edge数据库
  - cloud_db.sql  模拟云端mysql 表结构和数据
- docker-compose.yml
- Dockerfile
- requirements.txt
```

## 运行

### 运行flask web server

```
cd mqtt_edge
python app.py
```
可以看到终端打印web server启动的相关信息，服务默认监听IP和端口为`127.0.0.1:5000`

### 打开Web界面

在浏览器打开`127.0.0.1:5000`

可以看到操作界面。

### 模拟步骤

- 1 设定基础设置，指定broker的HOST和PORT，edge设备的sqlite所在路径。
- 2 启动云端。
- 3 填写`term_sn`和 `term_config`，启动edge设备。
- 4 切换到终端，可以看到 `e_edge on_connect`等信息，则表示服务启动成功。
- 5 edge设备注册。点击按钮之后，切换至终端，可以看到注册结果日志。如果出现‘非登记设备’，则说明该term_sn设备未在云端设备，所以可以‘添加edge设备到数据库’，完成再点击注册可以看到注册结果。
- 6 edge上报事件。会在消息区域自动提示“主题”和“消息”内容，点击发送可以进行上报。注意查看终端输出日志。
- 7 云端下发命令。会在消息区域自动提示“主题”和“消息”内容，点击发送可以进行下发，注意查看终端输出日志。
