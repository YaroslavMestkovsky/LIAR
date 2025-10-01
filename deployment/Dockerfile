# Контейнер с виртуальным окружением проекта.
FROM python:3.11.0
ARG USER_GID

# установка необходимых зависимостей
RUN apt update && apt upgrade -y

# настройка доступа к контейнеру по SSH
RUN apt-get install -y openssh-server sudo
RUN mkdir /var/run/sshd

RUN useradd -rm -d /home/python-root -s /bin/bash -g root -G sudo -u ${USER_GID} python-root && \
    echo 'python-root:python-root' | chpasswd

# установка зависимостей
COPY requirements.txt /opt/requirements.txt
RUN pip install --upgrade pip==25.2 && \
    pip install wheel && \
    pip install -r /opt/requirements.txt

# Отладка
#CMD ["tail", "-f", "/dev/null"]
