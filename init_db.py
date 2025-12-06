# here is used to setting DataBase
# if u have any visionable dataBase app, then dont use these

import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect("Weather.db")
conn.row_factory = sqlite3.Row

# info = ("19 - 22","5%","3","clouds",63)
# toDB = '''UPDATE weather SET temp = ?,rainfall = ?,uv = ?,cloudcover = ? Where cid = ?'''
# conn.execute(toDB,info)

# sql = '''select DISTINCT cID From City Order by cID ASC'''
# cid = conn.execute(sql).fetchall()
# for c in cid:
#     print(c[0])

# name = "桃園"
# x = (name,)
# sql = '''Select cID from City where name = ?'''
# cid = conn.execute(sql,x).fetchone()
# print(cid)
# cid = cid[0]
# print(cid)

# x = (cid,)
# sql = '''select * From weather Where cid = ?'''
# weather = conn.execute(sql,x).fetchall()
# for w in weather:
#     print(w['temp'],w['rainfall'],w['cloudcover'],w['uv'],w['windspeed'])

# x = ("Hua",)                                                      #選擇登入者的ID
# sub_sql = '''Select submit.Name, City.cID From submit LEFT JOIN City ON submit.Name = City.Name WHERE ID = ?'''
# cid = conn.execute(sub_sql,x).fetchall()

# for row in cid:
#     print(row[0])
#     print(row[1])

cache_sql = '''SELECT temp,cloudcover From weather WHERE cid = ?'''
cached_data = conn.execute(cache_sql,(100,)).fetchone()
if cached_data:
    print("work")
else:
    print("useless")
    
# test for fetch info

# conn.execute(sql,x)
conn.commit()
conn.close()