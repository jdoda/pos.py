# Copyright 2011 Jonathan Doda
#
# This file is part of pos.py.
#
# pos.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 3,
# as published by the Free Software Foundation.
#
# pos.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pos.py.  If not, see <http://www.gnu.org/licenses/>.

import struct


class KeyInputFile(object):
    
    def __init__(self, base_file):
        self.file = base_file
        self.input_event_st = struct.Struct('llHHi')
        self.charmap = {
            2   : '1',
            3   : '2',
            4   : '3',
            5   : '4',
            6   : '5',
            7   : '6',
            8   : '7',
            9   : '8',
            10  : '9',
            11  : '0',
            28  : '\n',
        }
    
    def fileno(self):
        return self.file.fileno()
       
    def read(self, size):
        chars_read = 0
        buf = ''
        while chars_read < size:
            in_buf = self.file.read(self.input_event_st.size)
            event = self.input_event_st.unpack(in_buf)
            if event[2] == 1 and event[4] == 0: # event is a key up event
                buf += self.charmap.get(event[3], '')
                chars_read += 1
        return buf
                
    def readline(self, size=None):
        chars_read = 0
        buf = ''
        while True:
            char = self.read(1)
            buf += char
            chars_read += 1
            if char == '\n' or (size != None and chars_read >= size):
                break
        return buf 
        
    def close(self):
        self.file.close()


def open_keys(path):
    base_file = open(path)
    return KeyInputFile(base_file)
    

if __name__ == '__main__':
    f = open_keys('/dev/input/event3')
    while True:
        print f.readline()    
