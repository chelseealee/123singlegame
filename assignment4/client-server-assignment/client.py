from network import Handler, poll
import sys
from threading import Thread
from time import sleep


myname = raw_input('What is your name? ')
users = []
users.append(myname)
class Client(Handler):
    
    def on_close(self):
        pass
    
    def on_msg(self, msg):
        if msg.has_key('join'):
            users.append(msg['join'])
            message = msg['join'] + " joined. Users: "
            for u in users:
                message+= u
                message+=" "
            print message
        elif msg.has_key('speak'):
            print msg['speak'] + ": " + msg['txt']
        elif msg.has_key('leave'):
            print msg['leave'] + " has left the chat"
        else:
            print msg
        
host, port = 'localhost', 8888
client = Client(host, port)
client.do_send({'join': myname})

def periodic_poll():
    while 1:
        poll()
        sleep(0.05)  # seconds
                            
thread = Thread(target=periodic_poll)
thread.daemon = True  # die when the main thread dies 
thread.start()

print myname + ' joined. Users: ' + myname

while 1:
    mytxt = sys.stdin.readline().rstrip()
    if mytxt == 'quit':
        client.close()
        break;
    else:
        client.do_send({'speak': myname, 'txt': mytxt})
