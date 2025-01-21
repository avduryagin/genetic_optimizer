FROM all-docker.asuproject.ru/base/ois-base-redos-python312:241217.1000.1-release AS cpp-build
COPY app/calclib/cpp /app

RUN dnf -y update && \
    dnf install -y gcc gcc-c++ make python3-devel libstdc++-static && \
    python3.12 -m pip install pybind11==2.13.6 && \
	python3.12 -m pip install --upgrade setuptools[core] && \
    dnf clean all && \
	python3.12 /app/setup.py build_ext --build-lib=/app/build

FROM all-docker.asuproject.ru/base/ois-base-redos-python312:241217.1000.1-release

COPY --chown=:0 --chmod=750 ./ /app
COPY --chown=:0 --chmod=750 --from=cpp-build /app/build /usr/local/lib/python3.12/lib-dynload

RUN chgrp 0 /app && chmod g=u /app && \
	python3.12 -m venv .venv && \
    python3.12 -m pip install --no-cache-dir -r /app/requirements/common.txt && \
    rm -rf /var/cache/dnf /var/cache/yum

EXPOSE 5000
WORKDIR /app
CMD ["gunicorn", "-w", "4", "--bind", "0.0.0.0:5000", "main:app_flask", "--timeout=600"]