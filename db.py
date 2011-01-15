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

