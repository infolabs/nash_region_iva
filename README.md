## Старт проекта 

Редактируем .env

`ROOT=C:\PycharmProjects\`

`DIRECTORY=C:\PycharmProjects\nash_region_iva\`

Собираем

`docker-compose build`

Запускаем

`docker-compose up`

Заходим в браузер 

`http://127.0.0.1:8000`

## Обновление данных
 
При старте контейнера автоматом качается база со стоп словами (запускается скрипт init.py)
если надо руками обновить его после старта - запускаем python3 и выполняем команды

`import nltk` 

`nltk.download('stopwords')` 

`nltk.download('punkt')`

При старте система синхронизирует из файла 
> nlproject/application/problems/new-clean.txt 

список актуальных проблем в базу, если надо обновить данные - перезаливаем этот файл и 
рестартуем контейнер

