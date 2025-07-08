FROM jupyter/docker-stacks-foundation

# 安装所需 Python 包
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 注册 IPython kernel
RUN python -m ipykernel install --user

# 拷贝 Python 服务器代码
COPY /src/ /srv/gateway/
WORKDIR /srv/gateway/

# 拷贝启动脚本
USER root
COPY run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh
USER $NB_UID

EXPOSE 8888

# 默认使用 bash 启动脚本
ENTRYPOINT ["/usr/local/bin/run.sh"]
