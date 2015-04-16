# internet-course
Internet course at UrFU

[![Code Climate](https://codeclimate.com/github/slogger/internet-course/badges/gpa.svg)](https://codeclimate.com/github/slogger/internet-course)

[Описание задач](http://anytask.urgu.org/course/38)

## sntp
Для запуска сервера, требуется `python 3.4` или выше

Запускаем сервер, по умолчанию на `5000` порту
```
python3 sntp-server.py [--delay смещение]
```

и просим клиента сходить к нам
```
python3 sntp-client.py -s localhost:5000
```

## tracert
Утилита показывая `traceroute` до какого нибудь хоста, по пути определяя номер автономной системы и страну маршрутизатора
```
sudo python3 tracert-as.py ya.ru
```
