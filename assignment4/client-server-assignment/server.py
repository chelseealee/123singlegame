from network import Listener, Handler, poll
import sys
import network
 
handlers = []
 
class MyHandler(Handler):
     
    def on_open(self):
        self.userName = "John Doe"
        handlers.append(self)
         
    def on_close(self):
        self.on_msg({'leave': self.userName})
        handlers.remove(self)
     
    def on_msg(self, msg):
        if msg.has_key('join'):
            self.userName = msg['join']
        for h in handlers:
            if h != self:
                h.do_send(msg)
 
class Server(object):
    
    def loop(self):
        port = 8888
        s = Listener(port, MyHandler)
        while 1:
            poll(timeout=0.05) # in seconds

server = Server()
server.loop()       
