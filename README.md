# NUL-SII-site-AI-service
## AI сервис для сайта НУЛ СИИ ИКИТ СФУ
***
### Требования к ПО:
1. Python=3.10
***
### Как запустить:
1. Установить виртуальное окружение
> Powershell:
> ```powershell
> py -3.10 -m venv venv
> ```

> Bash:
> ```bash
> python3.10 -m venv venv
> ```
2. Активировать виртуальное окружение
> Powershell:
> ```powershell
> ./venv/scripts/activate.ps1
> ```

> Bash:
> ```bash
> source venv/bin/activate
> ```
3. Обновить pip
> Powershell:
> ```powershell
> python -m pip install --upgrade pip
> ```

> Bash:
> ```bash
> -
> ```
4. Установить библиотеки
> Powershell:
> ```powershell
> pip install -r requirements.txt
> ```

> Bash:
> ```bash
> -
> ```
5. Запустить тестовый сервер
> Powershell:
> ```
> uvicorn main:app --reload --host 127.0.0.1 --port 8080 
> ```

> Bash:
> ```
> -
> ```
***
### Пути проекта:
1. WebRTC:
> Документация:\
> OpenAPI: webrtc/docs\
> ReDoc: webrtc/redoc

> Проекты:\
> Тестовая HTML страница (GET, text/html): webrtc/[project_name]/page\
> JS скрипт для создания подключения (GET, text/javascript): webrtc/[project_name]/script\
> Сюда отправлять запрос на подключение (POST, application/json): webrtc/[project_name]/offer

2. Photo:
> Документация:\
> OpenAPI: photo/docs\
> ReDoc: photo/redoc

> Проекты: [пока не точно]\
> Тестовая HTML страница (GET): photo/[project_name]/page\
> JS скрипт для создания подключения (GET): photo/[project_name]/script\
> Сюда отправлять запрос на обработку (POST): photo/[project_name]/offer
***
### Реализованные проекты:
#### WebRTC:
1. Тестовый проект для проверки подключения: webrtc/test
2. Фурдилов Д.М., Обнаружение пересечения опасный зон... (пока без опасных зон🥲): webrtc/dedsad
