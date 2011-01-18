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

#scanner_device_path = '/dev/input/by-id/usb-Metrologic_Metrologic_Scanner-event-kbd'
scanner_device_path = '/dev/null'
database_uri = 'sqlite:///home/guest/pos.db'
special_buttons = {
    'Water'   :'055100300017', 
    'Nestea'  :'839093', 
    'Snickers':'058496814595',
    'Coke'    :'678290', 
    'Arizona' :'613008722579',
}
