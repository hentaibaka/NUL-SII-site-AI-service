# Инструкция по развёртыванию на сервере 
***
## Инструкция работает со следующей конфигурацией:
* Ubuntu 22.04 LTS 64-bit
* Python 3.10
* Оперативная память >= 5Гб (при 4Гб сервер может выдержать только 1 подключение по WebRTC, при нескольких подключениях происходят постоянные реконнекты) 
* Дисковое хранилище >= 16Гб
* Ядра процессора - я тестировал на VPS от Селектел с 8 ядрами, не знаю какие там процессоры, но сервер еле-еле выдерживал 2 единовременных подключения
***
## Все действия выполнялись под root пользователем
1. Загрузка репозитория в /var/www
>Bash:
>```bash
>mkdir /var/www
>cd /var/www
>apt install git
>git clone https://github.com/hentaibaka/NUL-SII-site-AI-service.git
>```
2. Установка виртуального окружения и зависимостей
>Bash
>```bash
>cd NUL-SII-site-AI-service
>apt install python3.10-venv
>python3 -m venv venv
>source venv/bin/activate
>pip3 install -r requirements.txt
>apt-get install ffmpeg libsm6 libxext6
>```
3. 777 права на папку репозитория\
Я не уверен в правильности данного действия, но я не знаю какие права выдать правильно, поэтому выдаю все. :D\
Владельцем директории является root, но процесс демон запускается от лица пользователя www\
Плюс Python-скрипт создаёт файл `ai-sevice.log` и записывает в него логи, у меня выдавало ошибку если я давал права только на `aiservice.sh`\
Файл создаваётся не из моего кода, а средствами библиотеки `logging`, а я не до конца рабираюсь как работают права, поэтому 777 всему голова
>Bash:
>```bash
>chmod 777 -R /var/www/NUL-SII-site-AI-service
>```
5. Создание процесса демона
>Bash:
>```bash
>adduser www
>nano /etc/systemd/system/aiservice.service
>chmod 775 /etc/systemd/system/aiservice.service
>systemctl daemon-reload
>systemctl enable aiservice
>systemctl start aiservice
>```
Содержимое `aiservice.service`
>```bash
>[Unit]
>Description=aiservice uvicorn daemon
>After=network.target
>
>[Service]
>User=www
>Group=www
>WorkingDirectory= /var/www/NUL-SII-site-AI-service
>ExecStart= /var/www/NUL-SII-site-AI-service/aiservice.sh
>Restart=on-failure
>
>[Install]
>WantedBy=multi-user.target
>```
5. Проксирование на `localhost`
В файле `/var/www/NUL-SII-site-AI-service/aiservice.sh` заданы параметры `--host 127.0.0.1` и `--port 8001` - `(127.0.0.1:8001)`\
Необходимо с помощью nginx перенаправить запросы с внешнего ip-адресса на `127.0.0.1:8001`\
Причём, необходимо подключить `ssl` сертификат, поскольку большинство браузеров позволяют сайту получить доступ к камере и микрофону только по `https`\
Базовый конфиг `nginx` с проксированием `http` запроса на `localhost`:
>```bash
>server {
>  listen 80; 
>  server_name <domain>;
>  location / {
>    proxy_pass http://127.0.0.1:8001;
>  }
>}
>```
***
Все логи записываются в `/var/www/NUL-SII-site-AI-service/ai-service.log`, этот файл мне нужен будет после завершения тестирования\
Я немного облажался с настройкой логгирования (а сил переделывать у меня нет), поэтому файл может быть неприлично большого размера
