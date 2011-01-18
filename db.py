# Copyright 2008 Jonathan Doda
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

from sqlobject import *
import config

connection = connectionForURI(config.database_uri)
sqlhub.processConnection = connection


class Item(SQLObject):
    upc = StringCol(notNull=True)
    name = StringCol(notNull=True)
    price = FloatCol(notNull=True)
    upc_index = DatabaseIndex(upc, unique=True)
    
    
class Sale(SQLObject):
    time = DateTimeCol(notNull=True)
    type = EnumCol(enumValues=['PURCHASE', 'SHRINKAGE', 'GIVEAWAY'], notNull=True)
    time_index = DatabaseIndex(time, unique=True)


class SaleItem(SQLObject):
    sale = ForeignKey('Sale', notNull=True)
    item = ForeignKey('Item', notNull=True)
    price = FloatCol(notNull=True)    

    
class Box(SQLObject):
    upc = StringCol(notNull=True)
    item = ForeignKey('Item', notNull=True)
    quantity = IntCol(notNull=True)
    cost = FloatCol(notNull=True)
    upc_index = DatabaseIndex(upc, unique=True)
    
    
class Purchase(SQLObject):
    time = DateTimeCol(notNull=True)    
    time_index = DatabaseIndex(time, unique=True)
    

class PurchaseBox(SQLObject):
    purchase = ForeignKey('Purchase', notNull=True)
    box = ForeignKey('Box', notNull=True)
    cost = FloatCol(notNull=True)
 

if __name__ == '__main__':    
    Item.createTable()
    Sale.createTable()
    SaleItem.createTable()
    Box.createTable()
    Purchase.createTable()
    PurchaseBox.createTable()

