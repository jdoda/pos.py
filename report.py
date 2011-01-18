# Copyright 2009 Ken Struys
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

import db
import csv

p=[]
for item in db.Item.select():
    sales = db.SaleItem.select(db.SaleItem.q.itemID == item.id).filter(SaleItem.
    p.append((item.name, sales.count()))

p.sort(lambda x,y: x[1] - y[1])

csv.writer(open("report.csv", "wb")).writerows(p)
