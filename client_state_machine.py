"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
import json
import pygame
import time
import os
import random
import tkinter as tk
import tkinter.messagebox
import tkinter.font as tkFont
from racing import *
from snack_game_final import *
from snack_class_final import *
from snack_utils import *
from buff_class import *
from chat_utils import *
from game_menu import *
from Tanks_Improved import *

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.power_line = None
        self.racing = None
        self.tanks = None
        self.game_menu = None

    def get_my_idx(self):
        msg = json.dumps({"action": "get_idx"})
        mysend(self.s, msg)
        raw_recv = myrecv(self.s)
        recv = json.loads(raw_recv)
        return recv["index"]

    def get_num_of_members(self):
        msg = json.dumps({"action": "get_num_of_members"})
        mysend(self.s, msg)
        raw_recv = myrecv(self.s)
        print(raw_recv)
        recv = json.loads(raw_recv)
        return recv["get_num_of_members"]

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action": "connect", "target": peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with ' + self.peer + '\n'
            return True
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return False

    def disconnect(self):
        msg = json.dumps({"action": "disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg,member_list,chatting_interface,window):
        self.out_msg = ''
        
        # ==============================================================================
        # Once logged in, do a few things: get peer listing, connect, search
        # And, of course, if you are so bored, just go
        # This is event handling instate "S_LOGGEDIN"
        # ==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action": "time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action": "list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) is True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action": "search", "target": term}))
                    search_rslt = json.loads(myrecv(self.s))["results"][1:].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action": "poem", "target": poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"][1:].strip()
                    if len(poem) > 0:
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

                else:
                    self.out_msg += menu
                chatting_interface.insert('end','['+self.me+']: '+ 'says:')
                chatting_interface.insert('end',my_msg)
                chatting_interface.insert('end','')

            if len(peer_msg) > 0:

                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING
                    member_list.append(self.peer)
                    tk.messagebox.showinfo(title = 'Connect', message = 'You are connected with' + self.peer + '. Chat away!')



        elif self.state == S_CHATTING:
            if len(my_msg) > 0:  # my stuff going out
                mysend(self.s, json.dumps({"action": "exchange", "from": "[" + self.me + "]", "message": my_msg}))
                chatting_interface.insert('end','['+self.me+']: '+ 'says:')
                chatting_interface.insert('end',my_msg)
                chatting_interface.insert('end','')

                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
                    while len(member_list) != 1:
                        member_list.pop()
                        
                if my_msg == "start game":
                    self.out_msg = "Gaming request has been sent.\n"
                    self.state = S_REQUEST
                    tk.messagebox.showinfo(title = 'Game', message = 'Gaming request has been sent. Waiting for respones.')

            if len(peer_msg) > 0:
                # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    member_list.append(peer_msg['from'])
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                    member_list.pop()
                elif peer_msg['action'] == 'disconnect_fake':
                    member_list.remove(peer_msg['who'])
                    
                else:
                    if peer_msg["message"] == "start game":
                        self.state = S_REQUEST
                        judge = tk.messagebox.askyesno(title = 'Game' , message = 'Will you accept/decline the gaming request?')
                        if judge:
                            tk.messagebox.showinfo(title = 'Game',message = 'You have accepted the gaming request! Waiting for others to decide!')
                            self.proc('accept', '',member_list,chatting_interface,window)
                            
                        else:
                            tk.messagebox.showinfo(title = 'Game',message = 'You declined the gaming request')
                            self.proc('decline','',member_list,chatting_interface,window)
                        
                    chatting_interface.insert('end',peer_msg['from'] + ' says')
                    chatting_interface.insert('end',peer_msg['message'])
                    chatting_interface.insert('end','')

            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu

        
        
        # ==============================================================================



        # ==============================================================================
        # Start chatting, 'bye' for quit
        # This is event handling instate "S_CHATTING"
        # ==============================================================================

        # ==============================================================================
        # After one member requested to start game, everyone goes into this state.
        # This is event handling in state "S_REQUEST"
        # ==============================================================================
        elif self.state == S_REQUEST:
            # to be implemented with Tkinter later
            if len(my_msg) > 0:  # my stuff going out
                if my_msg == "accept" or my_msg == "decline":
                    mysend(self.s, json.dumps({"action": "request", "decision": my_msg}))
                    if my_msg == 'decline':
                        self.state = S_CHATTING
                

            if len(peer_msg) > 0:  # peer's stuff, coming in
                print("SM", 182)
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "publish":
                    if peer_msg["result"] == "accept":
                        self.out_msg += peer_msg["who"] + " accepted the game request.\n"
                        tk.messagebox.showinfo(title = 'Game', message = peer_msg['who'] + ' accepted the game request.')
                        
                    else:
                        self.out_msg += peer_msg["who"] + " declined the game request.\n"
                        self.out_msg += "Going back to chatting."
                        self.state = S_CHATTING
                        tk.messagebox.showinfo(title = 'Game', message = peer_msg['who'] + ' declined the game request.')
                if peer_msg["action"] == "approved":
                    self.out_msg = "Game request approved by all group members.\n"
                    self.out_msg = "Redirecting to the game choosing menu.\n"
                    tk.messagebox.showinfo(title = 'Game' , message = 'All the members have accepted. Game starts, enjoy!')
                    self.state = S_GAMEMENU
        # ==============================================================================
        # Gaming request has been approved by all group members. Next, to vote.
        # This is event handling in state "S_GAMEMENU"
        # ==============================================================================
        elif self.state == S_GAMEMENU:
            self.game_menu = GameMenu(self.s)
            success, peer_msg = self.game_menu.main_loop()  # got all info from server inside the main_loop()
            # to be implemented in Tkinter
            if not success:
                self.out_msg += "Some peer has quited the game menu."
                self.state = S_CHATTING
            else:
                if len(peer_msg) > 0:  # peer's stuff, coming in
                    peer_msg = json.loads(peer_msg)
                    if peer_msg["game"] == "power line":
                        self.state = S_POWERLINE
                        self.out_msg += "Initializing Power Line......"
                    elif peer_msg["game"] == "racing":
                        self.state = S_RACING
                        self.out_msg += "Initializing Racing......"
                    elif peer_msg["game"] == "tanks":
                        self.state = S_TANKS
                        self.out_msg += "Initializing Tanks......"
        # ==============================================================================
        # The First Game: Power Line; go into main game loop.
        # This is event handling in state "S_POWERLINE".
        # ==============================================================================
        elif self.state == S_POWERLINE:
            # implemented by pygame
            num_of_members = self.get_num_of_members()
            my_idx = self.get_my_idx()
            self.power_line = SnackGame(self.s, my_idx)  # .__init__(self.s, my_idx)
            self.power_line.set_window(num_of_members)
            self.power_line.game_loop()
            self.state = S_CHATTING
            mysend(self.s, json.dumps({"action": "exchange", "from": "[" + self.me + "]",
                                       "message": 'Game ends! You are back in the chatting with your peers.'}))
            self.out_msg += 'Game ends! You are back in the chatting with your peers.'
        # ==============================================================================
        # The Second Game: Racing; go into main game loop.
        # This is event handling in state "S_RACING".
        # ==============================================================================
        elif self.state == S_RACING:
            # TODO: implemented by pygame
            self.racing = Racing(self.s)
            self.racing.game_loop()
            self.state = S_CHATTING
            self.out_msg += 'Game ends! You are back in the chatting with your peers.'
        # ==============================================================================
        # The Third Game: Racing; go into main game loop.
        # This is event handling in state "S_TANKS".
        # ==============================================================================
        elif self.state == S_TANKS:
            # TODO: implemented by pygame
            self.tanks = Tanks(self.s)
            self.tanks.game_loop()
            self.state = S_CHATTING
            self.out_msg += 'Game ends! You are back in the chatting with your peers.'
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

