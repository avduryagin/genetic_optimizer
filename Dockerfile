FROM all-docker.asuproject.ru/base/ois-base-redos-python312:240927.1500.1-release
RUN dnf -y update
RUN dnf groupinstall -y "Development Tools"
WORKDIR /app
COPY requirements/common.txt /root/app/

RUN python3.12 -m venv .venv && \
    pip install -r /root/app/common.txt
RUN python3.12 -m pip  install --upgrade setuptools[core]
COPY app/calclib/cpp /root/app/cpp

RUN python3.12 /root/app/cpp/setup.py build_ext --build-lib=/usr/local/lib/python3.12/lib-dynload
COPY . ./

EXPOSE 5000
CMD python server.py

#docker run --mount type=bind,source="$(pwd)"/app/calclib/cpp,target=/app/app/calclib/cpp mydocker
#docker exec -it d3070ec72d81  /bin/bash
#docker ps --format 'CONTAINER ID : {{.ID}} | Name: {{.Names}} | Image:  {{.Image}} |  Ports: {{.Ports}}'
#docker container ps
#python /app/app/calclib/py/test.py