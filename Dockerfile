FROM quay.io/jupyter/pytorch-notebook:cuda12-latest

# 安装所需 Python 包
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 拷贝 Python 服务器代码
COPY /src/ /srv/gateway/
WORKDIR /srv/gateway/

# 拷贝启动脚本
USER root
COPY run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh
USER $NB_UID

ENV PYDEVD_DISABLE_FILE_VALIDATION=1

EXPOSE 8888

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -sf http://localhost:8888/isReady | grep -q "ready" || exit 1

# 默认使用 bash 启动脚本
ENTRYPOINT ["/usr/local/bin/run.sh"]
