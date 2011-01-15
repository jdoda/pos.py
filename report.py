import db
import csv

p=[]
for item in db.Item.select():
    sales = db.SaleItem.select(db.SaleItem.q.itemID == item.id).filter(SaleItem.
    p.append((item.name, sales.count()))

p.sort(lambda x,y: x[1] - y[1])

csv.writer(open("report.csv", "wb")).writerows(p)
