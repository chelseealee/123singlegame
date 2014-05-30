"""
Tkinter resources: 
http://zetcode.com/gui/tkinter/introduction/
https://github.com/siddharthasahu/P2P-chat-application
https://docs.python.org/2/library/tkinter.html
http://www.tkdocs.com/tutorial/grid.html
"""
from network import Handler, poll
import random
import string

import Tkinter as tk


myname = ''.join([random.choice(string.ascii_lowercase + string.digits) 
                  for _ in range(4)])

class MyGUI():
    
    def __init__(self, manager):
        self.manager = manager
        root = tk.Tk()  # main window
        root.protocol('WM_DELETE_WINDOW', self.manager.stop)  # cross was clicked
        root.title('Chat client')
        root.resizable(width=False, height=False)
        self.root = root
        self._build_gui()
        
    def _build_gui(self):
        root = self.root
        root.grid()
        
        self.chat_screen = tk.Text(root, bg="white", width=60, height=20,
                                   state=tk.DISABLED, wrap=tk.WORD)
        self.chat_screen.grid(column=0, row=0, sticky=tk.EW)
        
        scrollbar = tk.Scrollbar(command=self.chat_screen.yview,
                                 orient=tk.VERTICAL)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.chat_screen.config(yscrollcommand=scrollbar.set)
        
        frame = tk.Frame(root)
        frame.grid(column=0, row=1, sticky=tk.EW)
        
        self.entry = tk.Entry(frame, width=60)
        self.entry.pack(side=tk.LEFT, padx=20)
        # ways to capture key press: http://stackoverflow.com/a/19148324/856897
        self.entry.bind('<Key>', lambda k: self._on_keypress(k))
        self.entry.focus_set()
        
        self.listbox = tk.Listbox(root, width=20)
        self.listbox.grid(column=2, row=0, sticky=tk.NSEW)
        
        
    def _on_keypress(self, key):
        # detect line feed/carriage return
        if key.char in ('\n', '\r') or key.keycode == 2359309: 
            txt = self.entry.get()
            self.entry.delete(0, tk.END)
            self.manager.network.send_msg(txt)
            self.show_msg(txt, myname)
            
    def show_msg(self, txt, author=None):
        txtbox = self.chat_screen
        txtbox.config(state=tk.NORMAL)
        if author:
            txtbox.insert(tk.END, author + ': ')
        txtbox.insert(tk.END, txt + '\n')
        txtbox.see(tk.END)
        txtbox.config(state=tk.DISABLED)
    
    def update_userlist(self, names):
        box = self.listbox
        box.delete(0, tk.END)
        [box.insert(tk.END, name) for name in names]
    
    def update(self):
        self.root.update()
    
    def kill(self):
        self.root.destroy()

class MyHandler(Handler):
    
    def __init__(self, manager):
        host, port = 'localhost', 8888
        Handler.__init__(self, host, port)
        self.manager = manager
        self.do_send({'join': myname})
        
    def on_close(self):
        self.manager.gui.show_msg('Server is offline.')
        self.manager.gui.show_msg('Close and re-open the window to restart.')
        
    def on_msg(self, msg):
        if 'join' in msg:
            self.manager.gui.update_userlist(msg['users'])
            name = msg['join']
            if name == myname:
                self.manager.gui.show_msg('welcome, ' + name)
            else:
                self.manager.gui.show_msg(name + ' joined')
        elif 'leave' in msg:
            self.manager.gui.update_userlist(msg['users'])
            self.manager.gui.show_msg(msg['leave'] + ' left')
        elif 'speak' in msg and msg['speak'] != myname:
            self.manager.gui.show_msg(msg['txt'], msg['speak'])
            
    def send_msg(self, txt):
        self.do_send({'speak': myname, 'txt': txt})
        
    def update(self):
        poll(0.01)
        
    def kill(self):
        self.close()  # will call on_close

class Manager():
    
    def __init__(self):
        self.gui = MyGUI(self)
        self.network = MyHandler(self)
        self.run()
    
    def run(self):
        self.keep_going = True
        while self.keep_going:
            self.network.update()
            self.gui.update()
        self.gui.kill()
        self.network.kill()
        
    def stop(self):
        self.keep_going = False

if __name__ == '__main__':
    Manager()