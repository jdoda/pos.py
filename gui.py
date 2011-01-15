import os, sys
import datetime
import pygtk
import gobject, gtk, gtk.glade

import db, keyinput


ROOT = sys.path[0]
SCANNER_DEV_PATH = '/dev/input/by-id/usb-Metrologic_Metrologic_Scanner-event-kbd'
#SCANNER_DEV_PATH = '/dev/input/event3'

def format_float(column, cell, model, iter):
    data = model.get_value(iter, 2)
    text = '%.2f' % data
    cell.set_property('text',text)
        
def parse_multiplication(string):
    operands = string.split('*')
    
    result = float(operands[0])
    for operand in operands[1:]:
        result *= float(operand)
    return result


class WidgetWrapper(object):
    """
    WidgetWrapper contains all of the boilerplate code that is needed to set up
    a glade based gui. It loads the glade xml, autoconnects the signals, and
    adds each widget as an attribute of the WidgetWrapper object.
    """
    
    def __init__(self, app, glade_file):
        self._xml = gtk.glade.XML(glade_file)
        self._xml.signal_autoconnect(app)
        
        self._widgets = []
        for widget in self._xml.get_widget_prefix(''):
            self._widgets.append(widget)
            setattr(self, widget.get_name(), widget)
            
    def __iter__(self):
        return self._widgets.__iter__()
    
    
class Window(object):
    
    def __init__(self):
        self.widgets = WidgetWrapper(self, os.path.join(ROOT, 'window.glade'))
        
        self.item_list = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_FLOAT, gobject.TYPE_INT)
        self.widgets.item_treeview.set_model(self.item_list)
        for index, name in enumerate(['UPC', 'Name', 'Price','Quantity']):
            cr = gtk.CellRendererText()
            column = gtk.TreeViewColumn(name, cr, text=index)
            column.pack_start(cr)
            if name == 'Price':
                column.set_cell_data_func(cr,format_float)
            self.widgets.item_treeview.append_column(column)
            
        self.box_list = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_FLOAT)
        self.widgets.box_treeview.set_model(self.box_list)
        for index, name in enumerate(['UPC', 'Item', 'Quantity', 'Cost']):
            cr = gtk.CellRendererText()
            column = gtk.TreeViewColumn(name, cr, text=index)
            column.pack_start(cr)
            
            self.widgets.box_treeview.append_column(column)
        
        self.special = {}
        infile = open(os.path.join(ROOT,'buttons.conf'))
        line = infile.readline()[:-1]
        while line:
            name, upc = line.split(',')
            self.special[name] = upc
            line = infile.readline()[:-1]
        infile.close()
        
        special_buttons = [
            self.widgets.special_button0,
            self.widgets.special_button1,
            self.widgets.special_button2,
            self.widgets.special_button3,
            self.widgets.special_button4,
        ]
        
        for i, k in enumerate(self.special.keys()):
            special_buttons[i].set_label(k)
        
        self.scanner_device = keyinput.open_keys(SCANNER_DEV_PATH)
        gobject.io_add_watch(self.scanner_device, gobject.IO_IN, self.on_scanner_device_input)
        
        self.item_list.append(('', 'Total', 0, 0))
        self.widgets.item_entry.grab_focus()

    def add_item(self,upc):
        items = db.Item.select(db.Item.q.upc == upc)
        if items.count():
            item = items[0]
            found = False
            for i,item_check in enumerate(self.item_list):
                if upc == item_check[0]:
                    found = True
                    new_upc = item_check[0]
                    new_name = item_check[1]
                    new_quantity = item_check[3] + 1
                    new_price = item.price * new_quantity
                    self.item_list[i] = (new_upc, new_name, new_price, new_quantity)
                    break
            if not found:
                self.item_list.prepend((item.upc, item.name, item.price,1))
        self.reset_total()
    
    def remove_item(self,upc):
        items = db.Item.select(db.Item.q.upc == upc)
        if items.count():
            item = items[0]
            for i, item_check in enumerate(self.item_list):
                if item_check[0] == upc:
                    if item_check[3] > 1:
                        new_upc = item_check[0]
                        new_name = item_check[1]
                        new_quantity = item_check[3] - 1
                        new_price = item.price * new_quantity
                        self.item_list[i] = (new_upc, new_name, new_price, new_quantity)
                    else:
                        self.item_list.remove(item_check.iter)
                    break
        self.reset_total()
        
    def reset_total(self):
        # remove the current total
        self.item_list.remove(self.item_list[-1].iter) 
        
        # recalulate and reinsert
        total = 0
        quantity = 0
        for item in self.item_list:
            total += item[2]
            quantity += item[3]
        self.item_list.append(('', 'Total', total, quantity))
        
    def on_item_treeview_key_press_event(self, widget, event):
        key = gtk.gdk.keyval_name(event.keyval)
        treeselection = self.widgets.item_treeview.get_selection()
        model, iter = treeselection.get_selected()
        upc = None
        if iter:
            upc = self.item_list.get_value(iter,0)
        if upc:
            if key == 'BackSpace' or key == 'Delete' or key == 'minus':
                self.remove_item(upc)
            if key == 'equal':
               self.add_item(upc)
    
    def on_special_add_clicked(self,button):
        upc = self.special[button.get_label()]
        if self.widgets.add_item_radiobutton.get_active():
            self.add_item(upc)
        else:
            self.remove_item(upc)
        self.widgets.item_entry.grab_focus()
    
    def on_item_entry_activate(self, *args):
        upc = self.widgets.item_entry.get_text()

    	if upc == '001':
    	    self.on_confirm_button_clicked()
    	    self.widgets.item_entry.set_text('')
    	    return
        
        if self.widgets.add_item_radiobutton.get_active():
                self.add_item(upc)
        else:
            self.remove_item(upc)
                    
        self.widgets.item_entry.set_text('')

    def on_confirm_button_clicked(self, *args):
        sale = db.Sale(time=datetime.datetime.now(), type='PURCHASE')
        for i in self.item_list:

            while i[3] and i[0]: 
                item = db.Item.select(db.Item.q.upc == i[0])[0]
                sale_item = db.SaleItem(sale=sale, item=item, price=item.price)
                i[3] -= 1

        self.item_list.clear()
        self.item_list.append(('', 'Total', 0, 0))
        self.widgets.item_entry.grab_focus()
    
    def on_box_entry_activate(self, *args):
        upc = self.widgets.box_entry.get_text()
        
        if self.widgets.add_box_radiobutton.get_active():
            boxes = db.Box.select(db.Box.q.upc == upc)
            if boxes.count():
                box = boxes[0]
                self.box_list.prepend((box.upc, box.item.name, box.quantity, box.cost))
        else:
            for box in self.box_list:
                if box[0] == upc:
                    self.box_list.remove(box.iter)
                    break
                    
        self.widgets.box_entry.set_text('')
        
    def on_box_confirm_button_clicked(self, *args):
        purchase = db.Purchase(time=datetime.datetime.now())
        for b in self.box_list:
            box = db.Box.select(db.Box.q.upc == b[0])[0]
            purchase_box = db.PurchaseBox(purchase=purchase, box=box, cost=box.cost)
        self.box_list.clear()
        self.widgets.box_entry.grab_focus()
    
    def on_item_UPC_entry_activate(self, *args):
        upc = self.widgets.item_UPC_entry.get_text()
        items = db.Item.select(db.Item.q.upc == upc)
        if items.count():
            item = items[0]
            self.widgets.item_name_entry.set_text(item.name)
            self.widgets.item_price_entry.set_text(str(item.price))
        
    def on_add_item_button_clicked(self, *args):
        upc = self.widgets.item_UPC_entry.get_text()
        name = self.widgets.item_name_entry.get_text()
        price = float(self.widgets.item_price_entry.get_text())
        
        items = db.Item.select(db.Item.q.upc == upc)
        if items.count():
            item = items[0]
            item.set(name=name, price=price)
        else:
            new_item = db.Item(upc=upc, name=name, price=price)
        
        self.widgets.item_UPC_entry.set_text('')
        self.widgets.item_name_entry.set_text('')
        self.widgets.item_price_entry.set_text('')
        self.widgets.item_UPC_entry.grab_focus()
    
    def on_box_UPC_entry_activate(self, *args):
        upc = self.widgets.box_UPC_entry.get_text()
        boxes = db.Box.select(db.Box.q.upc == upc)
        if boxes.count():
            box = boxes[0]
            self.widgets.box_item_entry.set_text(box.item.upc)
            self.widgets.box_quantity_entry.set_text(str(box.quantity))
            self.widgets.box_cost_entry.set_text(str(box.cost))
        
    def on_add_box_button_clicked(self, *args):
        upc = self.widgets.box_UPC_entry.get_text()
        item_upc = self.widgets.box_item_entry.get_text()
        item = db.Item.select(db.Item.q.upc == item_upc)[0]
        quantity = int(self.widgets.box_quantity_entry.get_text())
        cost = parse_multiplication(self.widgets.box_cost_entry.get_text())
        
        boxes = db.Box.select(db.Box.q.upc == upc)
        if boxes.count():
            box = boxes[0]
            box.set(item=item, quantity=quantity, cost=cost)
        else:
            new_box = db.Box(upc=upc, item=item, quantity=quantity, cost=cost)
        
        self.widgets.box_UPC_entry.set_text('')
        self.widgets.box_item_entry.set_text('')
        self.widgets.box_quantity_entry.set_text('')
        self.widgets.box_cost_entry.set_text('')
        self.widgets.box_UPC_entry.grab_focus()
    
    def on_scanner_device_input(self, *args):
        upc = self.scanner_device.readline()[:-1]
        if self.widgets.add_item_radiobutton.get_active():
            self.add_item(upc)
        else:
            self.remove_item(upc)
        self.widgets.item_entry.grab_focus()
        self.widgets.window.present()
        
        # We want the event again, so return True
        return True
    
    def on_window_destroy(self, *args):
        gtk.main_quit()

    
    
