#!/usr/bin/python

#Modified from http://voorloopnul.com/blog/a-python-proxy-in-less-than-100-lines-of-code/

import socket
import select
import time
import sys
import os
import sqlite3
 
# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 4096
delay = 0.0001
forward_ip = 'localhost'
threshold = 30 #60*60*24*5 #number of seconds before someone is a regular. In this case, 5 days

conn = sqlite3.connect('friendzone.db')
c = conn.cursor()
x = c.execute
showselect = c.fetchone
x("CREATE TABLE IF NOT EXISTS guests (ip varchar(15), time int)")
x("CREATE TABLE IF NOT EXISTS regulars (ip varchar(15))")
conn.commit()

underattack = False

 
class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception, e:
            print e
            return False
 
class TheServer:
    input_list = []
    channel = {}
    time = {}
 
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)
 
    def main_loop(self):
        global underattack
        self.input_list.append(self.server)
        while 1:
            time.sleep(delay)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [], .05)
            userinput = ss([sys.stdin,], [], [], 0.1)[0]
            if userinput:
                for file in userinput:
                    line = file.readline()
                    if not line: # EOF, remove file from input list
                      userinput.remove(file)
                    else:
                        strip = line.rstrip()
                        if strip == 'stop':
                            print "Goodbye"
                            time.sleep(1)
                            sys.exit(0)
                        elif strip == 'protect':
                            print "Protecting server" 
                            underattack = True
                        elif strip == 'relax':
                            print "No longer protecting server"
                            underattack = False
            for self.s in inputready:
                if self.s == self.server:
                    self.on_accept()
                    break
                try:
                    self.data = self.s.recv(buffer_size)
                except socket.error as e:
                    continue
                if len(self.data) == 0:
                    self.on_close()
                    break
                else:
                    self.on_recv()
 
    def on_accept(self):
        clientsock, clientaddr = self.server.accept() #the person who wants to connect
        if underattack:
            x("Select * from regulars where ip=?", (clientaddr[0],)) #if this ip is a regular connector
            result = showselect()
            if not result:
                clientsock.close()
                return #don't connect to main server
        forward = Forward().start(forward_to[0], forward_to[1])
        if forward:
            print clientaddr, "has connected"
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
            self.time[clientsock] = int(time.time())
        else:
            print "Can't establish connection with remote server.",
            print "Closing connection with client side", clientaddr
            clientsock.close()
 
    def on_close(self):
        t = int(time.time()) - self.time[self.s]
        name = False
        try:
            name = self.s.getpeername()
        except socket.error:
            print "no socket found"
        if name:
            print name , "has disconnected after " + str(t) + " seconds"
            x("select * from regulars where ip=?", (name[0],)) #first check if they are a regular
            result = showselect()
            if not result: #they aren't a regular"
                x("select * from guests where ip=?", (name[0],))
                result = showselect()
                if result:
                    oldtime = result[1]
                    newtime = t + oldtime
                    if newtime >= threshold:
                        x("insert into regulars values (?)", (name[0],))
                        x("delete from guests where ip=?", (name[0],))
                        conn.commit()
                    else:
                        x("update guests set time=? where ip=?", (newtime, name[0]))
                        conn.commit()
                else: #this is the first time they've connected
                    x("insert into guests values (?,?)", (name[0],t,))
                    conn.commit()
        #remove objects from input_list
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]
        # close the connection with client
        self.channel[out].close()  # equivalent to do self.s.close()
        # close the connection with remote server
        self.channel[self.s].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.s]
        del self.time[self.s]
 
    def on_recv(self):
        data = self.data
        try:
            self.channel[self.s].send(data)
        except socket.error:
            print "Couldn't send data"
 
if __name__ == '__main__':

    if len(sys.argv) != 3:
        print "proxy.py <port to listen> <port to forward>'"
        sys.exit(0)
    print "Guardian is now running."
    print "Type 'protect' to turn protection on"
    print "     'relax' to run protection off"
    print "     'stop' to end the program"
    port = int(sys.argv[1])
    forward_to = (forward_ip, int(sys.argv[2]))
    server = TheServer('', port)
    try:
        server.main_loop()
    except KeyboardInterrupt:
        print "Ctrl C - Stopping server"
        conn.commit()
        conn.close()
        sys.exit(1)






