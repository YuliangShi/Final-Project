import time
import socket
import select
import sys
import json
from chat_utils import *
import tkinter as tk
import tkinter.messagebox
import tkinter.font as tkFont
import client_state_machine as csm  # import client_state_machine_student as csm

import threading

class Client:
    def __init__(self, args):
        self.peer = ''
        self.console_input = []
        self.state = S_OFFLINE
        self.system_msg = ''
        self.local_msg = ''
        self.peer_msg = ''
        self.args = args
        self.window = tk.Tk()
        self.window_chatting = None

    def quit(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def get_name(self):
        return self.name

    def init_chat(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        svr = SERVER if self.args.d == None else (self.args.d, CHAT_PORT)
        self.socket.connect(svr)
        self.sm = csm.ClientSM(self.socket)
        reading_thread = threading.Thread(target=self.read_input)
        reading_thread.daemon = True
        reading_thread.start()

    def shutdown_chat(self):
        return

    def send(self, msg):
        mysend(self.socket, msg)

    def recv(self):
        return myrecv(self.socket)

    def get_msgs(self):
        read, write, error = select.select([self.socket], [], [], 0)
        my_msg = ''
        peer_msg = []
        # peer_code = M_UNDEF    for json data, peer_code is redundant
        if len(self.console_input) > 0:
            my_msg = self.console_input.pop(0)
        if self.socket in read:
            peer_msg = self.recv()
        return my_msg, peer_msg

    def output(self):
        if len(self.system_msg) > 0:
            print(self.system_msg)
            self.system_msg = ''

    def login(self,my_msg):
        if len(my_msg) > 0:
            self.name = my_msg
            msg = json.dumps({"action": "login", "name": self.name})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.state = S_LOGGEDIN
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(self.name)
                self.print_instructions()
                return (True)
            elif response["status"] == 'duplicate':
                self.system_msg += 'Duplicate username, try again'
                return False
        else:  # fix: dup is only one of the reasons
            return (False)

    def read_input(self):
        while True:
            text = sys.stdin.readline()[:-1]
            self.console_input.append(text)  # no need for lock, append is thread safe

    def print_instructions(self):
        self.system_msg += menu

    def run_chat(self):
        self.init_chat()
        self.system_msg += 'Welcome to ICS chat\n'
        self.system_msg += 'Please enter your name: '
        self.output()
        self.window_set(self.window)      
        self.system_msg += 'Welcome, ' + self.get_name() + '!'
        self.output()
        self.window_chatting = tk.Tk()
        self.window_chatting_set_up(self.window_chatting)

        self.quit()

    # ==============================================================================
    # main processing loop
    # ==============================================================================
    def window_set(self,window):

        try:
        

            window.title('Welcome to ICS Chat')
            window.geometry('450x300')

            # welcome image
            canvas = tk.Canvas(window, height=200, width=500)
            image_file = tk.PhotoImage(file='welcome.gif')
            image = canvas.create_image(0,0, anchor='nw', image=image_file)
            canvas.pack(side='top')

            # user information
            tk.Label(window, text='User name: ').place(x=50, y= 150)
            tk.Label(window, text='Password: ').place(x=50, y= 190)

            var_usr_name = tk.StringVar()
            entry_usr_name = tk.Entry(window, textvariable=var_usr_name)
            entry_usr_name.place(x=160, y=150)
            var_usr_pwd = tk.StringVar()
            entry_usr_pwd = tk.Entry(window)
            entry_usr_pwd.place(x=160, y=190)

            def usr_login():
                global destroy
                usr_name = var_usr_name.get()
                boolean = self.login(usr_name)
                if boolean:
                    tk.messagebox.showinfo(title = 'Welcome',message = 'Welcome! '+\
                                           usr_name+'\n'+'Happy Chatting!')
                    time.sleep(1)
                    window.destroy()
                    
                else:
                    tk.messagebox.showinfo(title = 'Error',message = 'Duplicate username, try again!')
        
            
            
            


        # login and sign up button
            btn_login = tk.Button(window, text='Login', command=usr_login)
            btn_login.place(x=170, y=230)
            btn_sign_up = tk.Button(window, text='Sign up')
            btn_sign_up.place(x=270, y=230)
            window.mainloop()
        except:
            return



    def window_chatting_set_up(self,window):
        try:
            window.title('Chatting Room')
            window.geometry('728x650')
            ft = tkFont.Font(family = 'Times',size = 15, weight = tkFont.BOLD)
            ft3 = tkFont.Font(family = 'Times',size = 12, weight = tkFont.BOLD)
            ft2 = tkFont.Font(family = 'Times',size = 12)
            canvas = tk.Canvas(window, height=728, width=728)
            image_file = tk.PhotoImage(file='chat_back.gif')
            image = canvas.create_image(0,0, anchor='nw', image=image_file)
            canvas.pack(side='top')
            rect_button = canvas.create_rectangle(550,100,718,450,fill = 'LightCyan')
            rect_input = canvas.create_rectangle(10,480,510,640,fill = 'LightCyan')
            tk.Label(window,text = 'Chat Partner:',font = ft,
                     bg = 'LightCyan').place(x= 555,y=105,)


            # list box

            label_name = self.sm.me
            front_label = tk.StringVar()

            front_label_set = 'Username: '+label_name+'    State: '+self.sm.state

            front_label.set(front_label_set)


            tk.Label(window,textvariable = front_label,
                     height = 1, width = 60,font = ft).place(x = 0, y = 25)

            # Quit
            def Quit():
                if self.sm.state == S_CHATTING:
                    judge = tk.messagebox.showinfo(title = 'Error',message = 'Please leave the gruop to quit!')
                judge = tk.messagebox.askyesnocancel(title = 'Quit',message = 'Are you sure to quit?')
                if judge:
                    tk.messagebox.showinfo(title = 'Quit',message = 'See you next time!')
                    self.sm.state = S_OFFLINE
                    window.destroy()

            tk.Button(window,text = 'Quit', font = ft3, height = 1,bg = 'Red',command = Quit).place(x= 650,y=25)





            chatting_interface = tk.Listbox(window,
                                            font =ft2,bg = 'LightCyan')


            s2 = tk.Scrollbar(window)
            chatting_interface.focus_set()
            s2.pack(side = 'right', fill ='y')
            chatting_interface.pack(side = 'left',fill ='y')
            s2.config(command = chatting_interface.yview)
            chatting_interface.config(yscrollcommand = s2.set)
            chatting_interface.place(x=10,y=100,width = 500, height = 350)
            s2.place(x=491,y=102,height =347)


            # Connect
            # LALALA



            partner_name = tk.StringVar()
            entry_partner = tk.Entry(window,textvariable = partner_name)
            entry_partner.place(x=555,y=135)
            def Connect():
                partner_name = entry_partner.get()
                if self.sm.state == S_CHATTING:
                    tk.messagebox.showinfo(title = 'Error',message = 'You are already chatting')
                else:
                    if self.sm.connect_to(partner_name) is True:
                        tk.messagebox.showinfo(title = 'Success',message = 'Successfully connected to '+partner_name+'! Chat away!')
                        member_list_set.append(partner_name)
                        mysend(self.sm.s, json.dumps({"action": "connect_middle",'to':partner_name}))
                        names = json.loads(myrecv(self.sm.s))['guys']
                        names = names.split(',')
                        self.sm.state = S_CHATTING
                        for i in names:
                            if len(i) != 0:
                                member_list_set.append(i)


                    else:
                        tk.messagebox.showinfo(title = 'Nope', message = 'Connection unsuccessful!')

            tk.Button(window,text = 'Connect',
                                       command = Connect, font = ft3,height = 1, bg = 'Yellow').place(x=630,y=165)

            tk.Label(window,text = 'Group Member:',font = ft,
                     bg = 'LightCyan').place(x= 555,y=205,)

            member_list = tk.StringVar()

            member_list_set = [self.sm.me]

            member_list.set(member_list_set)


            member_interface = tk.Listbox(window, listvariable = member_list,
                                          font = ft2, width = 15 , height = 6)
            member_interface.place(x = 585, y = 235)

            def Leave():
                if self.sm.state != S_CHATTING:
                    tk.messagebox.showinfo(title = 'Error', message = 'You are not chatting!')
                else:
                    judge = tk.messagebox.askyesnocancel(title = 'Leave', message = 'Are you sure to leave?')
                    if judge:
                        tk.messagebox.showinfo(title = 'Leave' , message = 'You has left your chat group.')
                        self.sm.proc('bye','',member_list_set,chatting_interface,window)


            button_leave = tk.Button(window,text= ' Leave  ',command = Leave, font = ft3,
                                     height = 1,bg = 'Yellow').place(x=630,y=370)

            input_interface = tk.Text(window,width = 62,height = 6,
                     font = ft2)
            s1 = tk.Scrollbar(window)
            input_interface.focus_set()
            s1.pack(side = 'right', fill ='y')
            input_interface.pack(side = 'left',fill ='y')
            s1.config(command = input_interface.yview)
            input_interface.config(yscrollcommand = s1.set)
            input_interface.place(x=10,y=480)
            s1.place(x=492,y=480,height =118)
            def Send():
                msg = input_interface.get(1.0,'end')
                if not type(msg) == str:
                    tk.messagebox.showinfo(title = 'Error', message = 'Cannot send empty message')
                else:
                    if len(msg) == 1:
                        tk.messagebox.showinfo(title = 'Error', message = 'Cannot send empty message')
                    if len(msg) > 1:
                        self.sm.proc(msg,'',member_list_set,chatting_interface,window)
                        input_interface.delete(1.0,'end')

            def Game():
                if self.sm.state != S_CHATTING:
                    tk.messagebox.showinfo(title = 'Error', message = 'You must be in the chatting group to play the game!')
                else:
                    self.sm.proc('start game','',member_list_set,chatting_interface,window)

            button_send = tk.Button(window,text='  Send  ',command = Send,font = ft3,
                                    height = 1,bg='Yellow').place(x = 440,y=605)

            button_game = tk.Button(window,text = 'Start Game', command = Game, font = ft3,
                                    height = 1,bg='Green').place(x = 585, y =405)


            while self.sm.state != S_OFFLINE:
                my_msg, peer_msg = self.get_msgs()
                self.sm.proc(my_msg,peer_msg,member_list_set,chatting_interface,window)
                member_list.set(member_list_set)
                front_label_set ='Username: '+label_name+'    State: '+self.sm.state
                front_label.set(front_label_set)
                chatting_interface.see('end')
                time.sleep(0.1)
                window.update()
        except:
            t = 0


            
            
            

                                                            

