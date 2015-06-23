package poplib

import (
    "bufio"
    "net"
)

type Client struct {
    conn net.Conn
    r *bufio.Reader
    w *bufio.Writer
}

type MessageList struct {
    ID int
    Size int
}

type MessageUidl struct {
    ID int
    UID string
}
