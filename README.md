# Jupyter Docker Server

## 简介

一个容器化的 Jupyter Notebook 服务器, 基于 Docker 镜像, 可以通过请求的方式在 Python 环境中运行并管理多个支持多种不同语言的 Jupyter Kernels。

## 快速开始

```bash
git clone git@github.com:fishshi/jupyter-docker-server.git
cd ./jupyter-docker-server
docker build -t jupyter-docker-server .
docker run -d -p 8888:8888 jupyter-docker-server
```

## API

### 0. 通用参数
- **kernelId**: 内核 Id, 用于唯一标识一个内核。
- **kernelName**: 内核名称, 用于指定该内核的语言。没有指定时使用默认值 `python3`。

### 1. 创建内核
- **接口地址**: `POST /start`
- **说明**: 根据请求体中的 `kernelId` 和 `kernelName`, 创建一个新的 Jupyter Kernel。如果对应 Id 的内核已经存在，则什么也不做。
- **请求体**:
```typescript
{
  "kernelId": string,
  "kernelName": string
}
```
- **响应体**:
```json
{
  "statusCode": 200
}
```
```json
{
  "statusCode": 500,
  "msg": "<Exception Message>"
}
```

### 2. 获取内核状态
- **接口地址**: `GET /getStatus/{kernelId}`
- **说明**: 根据 `kernelId`, 获取对应的 Jupyter Kernel 的状态。内核存在返回 `运行中`, 内核不存在返回 `已关闭`。
- **响应体**:
```json
{
  "statusCode": 200,
  "data": "运行中"
}
```
```json
{
  "statusCode": 200,
  "data": "已关闭"
}
```
```json
{
  "statusCode": 500,
  "msg": "<Exception Message>"
}
```

### 3. 关闭内核
- **接口地址**: `POST /shutdown`
- **说明**: 根据请求体中的 `kernelId`, 关闭对应的 Jupyter Kernel。如果对应 Id 的内核不存在，则什么也不做。
- **请求体**:
```typescript
{
  "kernelId": string
}
```
- **响应体**:
```json
{
  "statusCode": 200
}
```
```json
{
  "statusCode": 500,
  "msg": "<Exception Message>"
}
```

### 4. 重启内核
- **接口地址**: `POST /restart`
- **说明**: 根据请求体中的 `kernelId`, 重启对应的 Jupyter Kernel。如果对应 Id 的内核不存在，则根据 `kernelId` 和 `kernelName` 创建内核。
- **请求体**:
```typescript
{
  "kernelId": string,
  "kernelName": string
}
```
- **响应体**:
```json
{
  "statusCode": 200
}
```
```json
{
  "statusCode": 500,
  "msg": "<Exception Message>"
}
```

### 5. 执行代码
- **接口地址**: `POST /execute`
- **说明**: 根据请求体中的 `kernelId` 和 `code`, 选择对应的 Jupyter Kernel 执行指定代码。如果对应 Id 的内核不存在，则根据 `kernelId` 和 `kernelName` 创建内核并执行代码。流式返回执行结果。
- **请求体**:
```typescript
{
  "kernelId": string,
  "kernelName": string,
  "code": string
}
```
- **响应体**:  
  msg_type: 符合 Jupyter 协议的消息类型  
  content: msg_type 对应的内容  
  详见 [Jupyter 协议文档](https://jupyter-client.readthedocs.io/en/latest/messaging.html)
```typescript
{
  "msg_type": string,
  "content": {}
}
```

### 6. 中断执行
- **接口地址**: `POST /interrupt`
- **说明**: 根据请求体中的 `kernelId`, 中断对应 Jupyter Kernel 的执行。如果对应 Id 的内核不存在，则什么也不做。
- **请求体**:
```typescript
{
  "kernelId": string
}
```
- **响应体**:
```json
{
  "statusCode": 200
}
```
```json
{
  "statusCode": 500,
  "msg": "<Exception Message>"
}
```

## 高级补充说明

### 构建时可选项

#### 其它语言支持

系统支持通过构建镜像时的参数来指定额外的语言支持。下面是一个构建包含 Python、CPP 和 Java 语言支持服务的例子：

```bash
docker build -t jupyter-docker-server \
    --build-arg ENABLE_CPP_KERNEL=true \
    --build-arg ENABLE_JAVA_KERNEL=true \
    .
```

可选的语言支持、构建参数以及对应的内核名称如下表所示：

| 语言 | 构建参数           | 内核名称             |
| ---- | ------------------ | -------------------- |
| CPP  | ENABLE_CPP_KERNEL  | xcpp11 xcpp14 xcpp17 |
| JAVA | ENABLE_JAVA_KERNEL | java                 |

## 项目依赖

### 父镜像

[jupyter/pytorch-notebook:cuda12-latest](https://quay.io/jupyter/pytorch-notebook)

### 其它语言内核依赖

[xeus-cling](https://github.com/jupyter-xeus/xeus-cling)  
[jjava](https://github.com/dflib/jjava)
