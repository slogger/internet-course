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

## portscan
Уилита умеющая в TCP сканирование портов
```
python3 127.0.0.1 -tp all -m 5
```

```
usage: portscan.py [-h] [-a] [-t] [-p PORTS] [-m MULTITHREADING] target

portscan.py

positional arguments:
  target                The target(s) you want to scan (192.168.0.1)

optional arguments:
  -h, --help            show this help message and exit
  -a, --all             Enable this for full output
  -t, --tcpscan         Enable this for TCP scans
  -p PORTS, --ports PORTS
                        The ports you want to scan (21,22,80,24-42)
  -m MULTITHREADING, --multithreading MULTITHREADING
                        Thread count
```

## dns
Кэширующий DNS сервер
```
sudo python3 dns_server.py 8.8.4.4
```
