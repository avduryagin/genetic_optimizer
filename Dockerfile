FROM all-docker.asuproject.ru/base/ois-base-redos-python312:241217.1000.1-release AS cpp-build
COPY app/calclib/cpp /app

RUN dnf -y update && \
    dnf install -y gcc gcc-c++ make python3-devel libstdc++-static && \
    python3.12 -m pip install pybind11==2.13.6 && \
	python3.12 -m pip install --upgrade setuptools[core] && \
    dnf clean all && \
	python3.12 /app/setup.py build_ext --build-lib=/app/build

FROM all-docker.asuproject.ru/base/ois-base-redos-python312:241217.1000.1-release
WORKDIR /app
COPY requirements/common.txt /root/app/

RUN chgrp 0 /app && chmod g=u /app && \
	python3.12 -m venv .venv && \
    python3.12 -m pip install --no-cache-dir -r /root/app/common.txt

COPY --chown=:0 --chmod=750 ./ /app
COPY --chown=:0 --chmod=750 --from=cpp-build /app/build /usr/local/lib/python3.12/lib-dynload

EXPOSE 5000
#WORKDIR /app

ENV 'Security__OpenIdConnect__Audience'="gpn-pipe-dev"
#ENV 'Security__OpenIdConnect__Authority'="https://ois-hub.okd.asuproject.ru/"
ENV 'Security__OpenIdConnect__Authority'="https://ois-platform-hub-gpn-pipe-dev.okd.asuproject.ru"
ENV 'Security__OpenIdConnect__ClientId'="gpn-pipe-dev"
ENV 'Security__OpenIdConnect__ClientSecret'='cce2d332-34ec-4e2f-9b5d-5f03f422533a'

CMD ["gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "main:app_flask", "--timeout=600"]