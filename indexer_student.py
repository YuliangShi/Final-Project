# -*- coding: utf-8 -*-
"""
Created on Sat Jul  5 11:38:58 2014

@author: zzhang
"""
import pickle

class Index:
    def __init__(self, name):
        self.name = name
        self.msgs = [];
        self.index = {}
        self.total_msgs = 0
        self.total_words = 0
        
    def get_total_words(self):
        return self.total_words
        
    def get_msg_size(self):
        return self.total_msgs
        
    def get_msg(self, n):
        return self.msgs[n]
        
    # implement
    def add_msg(self, m):
        return
        
    def add_msg_and_index(self, m):
        self.add_msg(m)
        line_at = self.total_msgs - 1
        self.indexing(m, line_at)

    # implement
    def indexing(self, m, l):
        return

    # implement: query interface
    '''
    return a list of tupple. if index the first sonnet (p1.txt), then
    call this function with term 'thy' will return the following:
    [(7, " Feed'st thy light's flame with self-substantial fuel,"),
     (9, ' Thy self thy foe, to thy sweet self too cruel:'),
     (9, ' Thy self thy foe, to thy sweet self too cruel:'),
     (12, ' Within thine own bud buriest thy content,')]
              
    '''
    def search(self, term):
        msgs = []
        return msgs

class PIndex(Index):
    def __init__(self, name):
        super().__init__(name)
        roman_int_f = open('roman.txt.pk', 'rb')
        self.int2roman = pickle.load(roman_int_f)
        roman_int_f.close()
        self.load_poems()
        
        # implement: 1) open the file for read, then call
        # the base class's add_msg_and_index
    def load_poems(self):
       return
    
        # implement: p is an integer, get_poem(1) returns a list,
        # each item is one line of the 1st sonnet
    def get_poem(self, p):
        poem = []
        return poem

if __name__ == "__main__":
    sonnets = PIndex("AllSonnets.txt")
    # the next two lines are just for testing
    p3 = sonnets.get_poem(3)
    print(p3)
    s_love = sonnets.search("love")
