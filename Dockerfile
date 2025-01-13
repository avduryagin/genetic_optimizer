FROM all-docker.asuproject.ru/base/ois-base-redos-python312:241120.1448.1-release
#c++ compiler
RUN dnf -y update
RUN dnf groupinstall -y "Development Tools"

WORKDIR /app
COPY requirements/common.txt /root/app/

RUN python3.12 -m venv .venv
RUN python3.12 -m pip install -r /root/app/common.txt
#c++ compilations block
RUN python3.12 -m pip  install --upgrade setuptools[core]
RUN python3.12 -m pip  install pybind11==2.13.6

COPY app/calclib/cpp /root/app/cpp
RUN python3.12 /root/app/cpp/setup.py build_ext --build-lib=/usr/local/lib/python3.12/lib-dynload
COPY . ./
EXPOSE 5000

ENV 'Security__OpenIdConnect__Audience'="gpn-pipe-dev"
ENV 'Security__OpenIdConnect__Authority'="https://ois-hub.okd.asuproject.ru/"
ENV 'Security__OpenIdConnect__ClientId'="gpn-pipe-dev"
ENV 'Security__OpenIdConnect__ClientSecret'='e6cce105-a25b-4a88-aad5-7af2ba4e9e96'

CMD gunicorn -w 4 --bind 0.0.0.0:5000 main:app_flask --timeout=600
#CMD python server.py
#conda env path:
#/home/ois.ru/avduryagin/anaconda3/envs/optimizer/lib/python3.12/lib-dynload

#docker run --mount type=bind,source="$(pwd)"/app/calclib/cpp,target=/app/app/calclib/cpp mydocker
#docker exec -it d3070ec72d81  /bin/bash
#docker ps --format 'CONTAINER ID : {{.ID}} | Name: {{.Names}} | Image:  {{.Image}} |  Ports: {{.Ports}}'
#docker container ps
#python /app/app/calclib/py/test.py