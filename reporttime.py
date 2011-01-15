import db
import csv
import datetime

t=("date",)
for item in db.Item.select():
    t+= (item.name, )
p=[t]

initd = datetime.datetime(2008, 9, 8)
endd = datetime.datetime.today() + datetime.timedelta(2)

while initd <= endd:
    tt= (initd,)
    d={}
    for sale in db.Sale.select(db.AND(db.Sale.q.time >= initd, db.Sale.q.time < initd+datetime.timedelta(1))):
        for i in db.SaleItem.select(db.SaleItem.q.saleID == sale.id):
            d[i.item.name] = d.get(i.item.name,0) + 1

    for name in t[1:]:
        tt+=(d.get(name,0),)
    
    p.append(tt)
    initd += datetime.timedelta(1)

csv.writer(open("report.csv", "wb")).writerows(p)
