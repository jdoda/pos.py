# Copyright 2008 Jonathan Doda
# Copyright 2008 Andrei Karpathy
# Copyright 2008 Daniel Lister
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


import os, sys
import datetime
import pygtk
import gobject, gtk

import config
import db
import evdev


ROOT = sys.path[0]


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
    a builder based gui. It loads the builder xml, autoconnects the signals, and
    adds each widget as an attribute of the WidgetWrapper object.
    """
    
    def __init__(self, app, path):
        self._builder = gtk.Builder()
        self._builder.add_from_file(path)
        self._builder.connect_signals(app)
        
        self._widgets = []
        for widget in self._builder.get_objects():
            self._widgets.append(widget)
            try:
                setattr(self, gtk.Buildable.get_name(widget), widget)
            except TypeError:
                pass
            
    def __iter__(self):
        return self._widgets.__iter__()
    
    
class Window(object):
    
    def __init__(self):
        gtk.settings_get_default().set_property("gtk-button-images", True)
        self.widgets = WidgetWrapper(self, os.path.join(ROOT, 'pos.ui'))

        price_column = self.widgets.item_treeview.get_column(2)
        price_column.set_cell_data_func(price_column.get_cell_renderers()[0], format_float)
        
        cost_column = self.widgets.box_treeview.get_column(2)   
        cost_column.set_cell_data_func(cost_column.get_cell_renderers()[0], format_float)

        for name, upc, image_path in config.product_buttons:
            button = gtk.Button(name)
            button.connect('clicked', self.on_product_button_clicked, upc)
            if image_path:
                image = gtk.image_new_from_file(os.path.join(ROOT, image_path))
                button.set_image(image)
            self.widgets.product_buttonbox.pack_start(button)
            button.show()
        
        self.scanner_device = evdev.Device(config.scanner_device_path)
        gobject.io_add_watch(self.scanner_device, gobject.IO_IN, self.on_scanner_device_input)

        self.widgets.item_entry.grab_focus()

    def add_item(self,upc):
        items = db.Item.select(db.Item.q.upc == upc)
        if items.count():
            item = items[0]
            found = False
            for i,item_check in enumerate(self.widgets.item_liststore):
                if upc == item_check[0]:
                    found = True
                    new_upc = item_check[0]
                    new_name = item_check[1]
                    new_quantity = item_check[3] + 1
                    new_price = item.price * new_quantity
                    self.widgets.item_liststore[i] = (new_upc, new_name, new_price, new_quantity)
                    break
            if not found:
                self.widgets.item_liststore.prepend((item.upc, item.name, item.price,1))
        self.reset_total()
    
    def remove_item(self,upc):
        items = db.Item.select(db.Item.q.upc == upc)
        if items.count():
            item = items[0]
            for i, item_check in enumerate(self.widgets.item_liststore):
                if item_check[0] == upc:
                    if item_check[3] > 1:
                        new_upc = item_check[0]
                        new_name = item_check[1]
                        new_quantity = item_check[3] - 1
                        new_price = item.price * new_quantity
                        self.widgets.item_liststore[i] = (new_upc, new_name, new_price, new_quantity)
                    else:
                        self.widgets.item_liststore.remove(item_check.iter)
                    break
        self.reset_total()
        
    def reset_total(self):
        # remove the current total
        self.widgets.item_liststore.remove(self.widgets.item_liststore[-1].iter) 
        
        # recalulate and reinsert
        total = 0
        quantity = 0
        for item in self.widgets.item_liststore:
            total += item[2]
            quantity += item[3]
        self.widgets.item_liststore.append(('', 'Total', total, quantity))
        
    def on_item_treeview_key_press_event(self, widget, event):
        key = gtk.gdk.keyval_name(event.keyval)
        treeselection = self.widgets.item_treeview.get_selection()
        model, iter = treeselection.get_selected()
        upc = None
        if iter:
            upc = self.widgets.item_liststore.get_value(iter,0)
        if upc:
            if key == 'BackSpace' or key == 'Delete' or key == 'minus':
                self.remove_item(upc)
            if key == 'equal':
               self.add_item(upc)
    
    def on_product_button_clicked(self, button, upc):
        if self.widgets.add_item_radiobutton.get_active():
            self.add_item(upc)
        else:
            self.remove_item(upc)
        self.widgets.item_entry.grab_focus()
    
    def on_item_entry_activate(self, *args):
        upc = self.widgets.item_entry.get_text()
        
        if self.widgets.add_item_radiobutton.get_active():
            self.add_item(upc)
        else:
            self.remove_item(upc)
                    
        self.widgets.item_entry.set_text('')

    def on_confirm_button_clicked(self, *args):
        sale = db.Sale(time=datetime.datetime.now(), type='PURCHASE')
        for i in self.widgets.item_liststore:

            while i[3] and i[0]: 
                item = db.Item.select(db.Item.q.upc == i[0])[0]
                sale_item = db.SaleItem(sale=sale, item=item, price=item.price)
                i[3] -= 1

        self.widgets.item_liststore.clear()
        self.widgets.item_liststore.append(('', 'Total', 0, 0))
        self.widgets.item_entry.grab_focus()
    
    def on_box_entry_activate(self, *args):
        upc = self.widgets.box_entry.get_text()
        
        if self.widgets.add_box_radiobutton.get_active():
            boxes = db.Box.select(db.Box.q.upc == upc)
            if boxes.count():
                box = boxes[0]
                self.widgets.box_liststore.prepend((box.upc, box.item.name, box.quantity, box.cost))
        else:
            for box in self.widgets.box_liststore:
                if box[0] == upc:
                    self.widgets.box_liststore.remove(box.iter)
                    break
                    
        self.widgets.box_entry.set_text('')
        
    def on_box_confirm_button_clicked(self, *args):
        purchase = db.Purchase(time=datetime.datetime.now())
        for b in self.widgets.box_liststore:
            box = db.Box.select(db.Box.q.upc == b[0])[0]
            purchase_box = db.PurchaseBox(purchase=purchase, box=box, cost=box.cost)
        self.widgets.box_liststore.clear()
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
        event = self.scanner_device.get_event()
        
        focus_widget = self.widgets.window.get_focus()
        if (not self.widgets.window.has_toplevel_focus() or not isinstance(focus_widget, gtk.Entry)):
            if event.type == 1 and event.value == 0 and event.char:
                if event.char == '\n':
                    self.widgets.item_entry.activate()
                    self.widgets.item_entry.grab_focus()
                    self.widgets.window.present()
                else:
                    curtext = self.widgets.item_entry.get_text()
                    self.widgets.item_entry.set_text(curtext + event.char)
        # We want the event again, so return True
        return True
    
    def on_window_destroy(self, *args):
        gtk.main_quit()
    
