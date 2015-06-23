package main

import (
    "log"
    "os"
    b64 "encoding/base64"
    "regexp"
    "strconv"
    "github.com/olekukonko/tablewriter"
    "./poplib"
    "strings"
    "flag"
)

const layout = "Jan 1, 2000 at 3:14pm (MST)"

func check(e error) {
    if e != nil {
        log.Fatal("ERROR: ", e)
    }
}

func main() {
    var server string
    var port string
    var login string
    var pass string
    var serv string

    flag.StringVar(&server, "server", "pop.mail.ru", "is a pop server")
    flag.StringVar(&port, "port", "995", "is a port")
    flag.StringVar(&login, "login", "example@mail.ru", "is a pop server")
    flag.StringVar(&pass, "pass", "pass", "is a password")
    flag.Parse()

    serv  = server + ":" + port

    client, err := poplib.DialTLS(serv)
    check(err)
    log.Print("TLS OK")

    if err = client.Auth(login, pass); err != nil {
        log.Fatal(err)
    }
    log.Print("AUTH OK")

    msgList, err := client.ListAll()
    check(err)

    table := tablewriter.NewWriter(os.Stdout)
    table.SetHeader([]string{"#", "To", "From", "Date", "Length", "Subject"})

    msgFromAddrRegExp, _ := regexp.Compile("<([-@.a-zA-Z0-9]+)>")
    msgFromNameRegExp, _ := regexp.Compile("([-=?@.a-zA-Z0-9]+)<")

    for _, m := range msgList {
        msg, err := client.Top(m.ID, 0)
        check(err)
        var id string
        var size string
        var msg_to string
        var msg_from string
        var msg_subj string
        id = strconv.Itoa(m.ID)
        size = strconv.Itoa(m.Size)

        for _, to := range msg.Header["To"] {
            msg_to += to
        }

        for _, f := range msg.Header["From"] {
            s := strings.Split(f, " ")
            var sender string
            var piece string
            piece = s[0][10:len(s[0])-2]

            if !msgFromNameRegExp.MatchString(piece) {
                data, err := b64.StdEncoding.DecodeString(piece)
                check(err)
                sender = string(data)
                msg_from += sender + " " + s[1]
            } else {
                name := msgFromNameRegExp.FindStringSubmatch(f)
                addr := msgFromAddrRegExp.FindStringSubmatch(f)
                data, err := b64.StdEncoding.DecodeString(name[1][10:len(name[1])-2])
                check(err)
                msg_from = string(data) + " <" + addr[1] + ">"
            }
        }

        for _, _subj := range msg.Header["Subject"] {
            s := strings.Split(_subj, " ")
            var subj string
            for _, piece := range s {
                data, err := b64.StdEncoding.DecodeString(piece[10:len(piece)-2])
                check(err)
                subj += string(data)
            }
            msg_subj = subj
        }

        table.Append([]string{
            id,
            msg_to,
            msg_from,
            msg.Header["Date"][0],
            size,
            msg_subj})
    }
    table.Render()

    if err = client.Quit(); err != nil {
        log.Fatal(err)
    }
}
