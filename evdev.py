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

import os
import struct
import datetime


input_event_st = struct.Struct('llHHi')
        

class Event(object):
    
    def __init__(self, struct, charmap):
        self.time = datetime.datetime.utcfromtimestamp(struct[0] + struct[1] / 1000000.0)
        self.type = struct[2]
        self.code = struct[3]
        self.value = struct[4]
        if self.type == 1: # EV_KEY
            self.char = charmap.get(struct[3], '')
        else:
            self.char = None
        

class Device(object):
    
    def __init__(self, path):
        self.fd = os.open(path, 0)
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
    
    def __del__(self):
        self.close()
    
    def fileno(self):
        return self.fd
       
    def get_event(self):
        buf = os.read(self.fd, input_event_st.size)
        event = input_event_st.unpack(buf)
        return Event(event, self.charmap)

    def close(self):
        os.close(self.fd)

