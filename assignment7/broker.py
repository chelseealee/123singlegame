from network import Listener, Handler, poll


handlers = {}  # map client handler to user name
names = {} # map name to handler
subs = {} # map tag to handlers

def broadcast(msg):
    for h in handlers.keys():
        h.do_send(msg)


class MyHandler(Handler):
    
    def on_open(self):
        handlers[self] = None
        
    def on_close(self):
        name = handlers[self]
        del handlers[self]
        broadcast({'leave': name, 'users': handlers.values()})
        
    def on_msg(self, msg):
        if 'join' in msg:
            name = msg['join']
            handlers[self] = name
            names[name] = self
            broadcast({'join': name, 'users': handlers.values()})
        elif 'speak' in msg:
            name, txt = msg['speak'], msg['txt']
            txt_list = msg['txt'].split()
            broadcast_flag = True
            sent_to = []
            for s in txt_list:
                if s[0] == "@":
                    self.private_message(str(s), dict(msg))
                    sent_to.append(s[1:])
                    broadcast_flag = False
                if s[0] == "+":
                    self.subscribe(str(s), str(name))
                if s[0] == "#":
                    self.publish(str(s), dict(msg), sent_to)
                    broadcast_flag = False
                if s[0] == "-":
                    self.unsubscribe(str(s), str(name))
            if broadcast_flag == True:
                broadcast({'speak': name, 'txt': txt})
                
    def private_message(self, string, msg):
        names[string[1:]].do_send({'speak': str(msg['speak']), 'txt': str(msg['txt'])})
    
    def publish(self, string, msg, sent_to):
        send_list = subs['+' + string[1:]]#subs.get(string, [])
        if len(send_list) != 0:
            for user in send_list:
                if user != self and user not in sent_to:
                    names[user].do_send({'speak': str(msg['speak']), 'txt': str(msg['txt'])})
                
    def unsubscribe(self, string, user_name):
        for k in subs.keys():
            if k[1:] == string[1:]:
                subs['+' + string[1:]].discard(user_name)
            
    def subscribe(self, string, user_name):
        if string not in subs.keys():
            subs[string] = {user_name}
        else:
            subs[string].add(user_name)
    
    
        

Listener(8888, MyHandler)
while 1:
    poll(0.05)