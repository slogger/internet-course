# internet-course
Internet course at UrFU

[![Code Climate](https://codeclimate.com/github/slogger/internet-course/badges/gpa.svg)](https://codeclimate.com/github/slogger/internet-course)

[Описание задач](http://anytask.urgu.org/course/38)

## sntp
Для запуска сервера, требуется `python 3.4` или выше

Запускает сервер, по умолчанию на `5000` порту
```
python3 sntp-server.py [--delay смещение]
```

и просим клиента сходить к нам
```
python3 sntp-client.py -s localhost:5000
```
