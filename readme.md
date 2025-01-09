## В образ ois-base-redos-python312:240927.1500.1-release
## Установить компилятор g++ 
* groupinstall -y "Development Tools"
## Создание и активация venv
* python3.12 -m venv .venv
## Установить пакеты для расчетных библиотек
 * pip install -r /root/app/common.txt
## Установить пакеты сборки библиотек C++
* python3.12 -m pip  install --upgrade setuptools[core]
## Скомпилировать исходный код С++
* COPY app/calclib/cpp /root/app/cpp
* python3.12 /root/app/cpp/setup.py build_ext --build-lib=/usr/local/lib/python3.12/lib-dynload
 
 ## Запуск waitress сервера 
* python server.py
