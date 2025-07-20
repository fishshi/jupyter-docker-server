# Jupyter Docker Server

## 简介

一个容器化的 Jupyter Notebook 服务器, 基于 Docker 镜像, 可以通过请求的方式在一个 Python 环境中运行并管理多个 Jupyter Kernels。

## 快速开始

```bash
docker run -d -p 8888:8888 jupyter-docker-server
```

## API

### 1. 创建内核
- **接口地址**: `POST /start`
- **说明**: 根据请求体中的 `kernelId`, 创建一个新的 Jupyter Kernel。如果对应 Id 的内核已经存在，则什么也不做。
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
- **说明**: 根据请求体中的 `kernelId`, 重启对应的 Jupyter Kernel。如果对应 Id 的内核不存在，则创建内核。
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

### 5. 执行代码
- **接口地址**: `POST /execute`
- **说明**: 根据请求体中的 `kernelId` 和 `code`, 选择对应的 Jupyter Kernel 执行指定代码。如果对应 Id 的内核不存在，则创建内核并执行代码。流式返回执行结果。
- **请求体**:
```typescript
{
  "kernelId": string,
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

## 注意

空闲的内核 1h 后会自动停止, 该内核所有的上下文信息会被清除无法恢复。

## 父镜像

- [jupyter/pytorch-notebook:cuda12-latest](https://quay.io/jupyter/pytorch-notebook)

## 额外依赖

[jupyter_client](https://github.com/jupyter/jupyter_client)
[fastapi](https://github.com/fastapi/fastapi)
[uvicorn](https://github.com/encode/uvicorn)
