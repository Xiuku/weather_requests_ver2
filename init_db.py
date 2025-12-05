# here is used to setting DataBase
# if u have any visionable dataBase app, then dont use these

import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect("Weather.db")

# sql = '''DROP TABLE IF EXISTS User'''
# sql = '''Create Table User(
#          ID TEXT NOT NULL,
#          email TEXT NOT NULL UNIQUE)'''
# 創建User Table

sql = '''Select * From user'''
info = conn.execute(sql).fetchall()
print(info)

# city_name = "Taipei"
# today_str = datetime.now().strftime('%Y-%m-%d')

# cache_sql = '''SELECT temperature,cloudcover,Lastupdated From weather WHERE Name = ?'''
# cached_data = conn.execute(cache_sql,(city_name,)).fetchone()
# print(cached_data[0])
# weather_info = {}
# if cached_data and cached_data[2] == today_str:
#     weather_info = {
#         "name" : city_name,
#         "temp" : cached_data[0],
#         "weather" : cached_data[1],
#     }
# print(weather_info)
#測試抓取weather資料表

# name = 'NewTaipei'
# x = (name,)
# sql = '''Select Landsitu From City Where Name = ?'''
# name = conn.execute(sql,x).fetchone()[0]
# print(name)
# print(type(name))
#測試抓取Landsitu

# user_id = 'Hua'
# name = 'Taipei'
# x = (user_id,name)
# sql = '''INSERT INTO submit VALUES(?,?)'''                    #選擇登入者的ID
# # plus = conn.execute(sql,x)
# sql = '''Select * From submit'''
# show = conn.execute(sql).fetchall()
# print(show)
# # 測試抓取submit資料表

# cities = []
# user_id = "Hua"
# x = (user_id,)
# sql = '''Select Name From submit WHERE ID = ?'''                    #選擇登入者的ID
# name = conn.execute(sql,x).fetchall()
# for n in name:                                                      #從資料庫中添加需顯示城市
#     cities.append({"name":n[0],"temp":26,"icon_url":"/static/assets/clear.png"})
# for c in cities:
#     print(c)
#測試訂閱城市的快訊

# x = ("Hua",)
# sql = '''Select submit.Name, City.Landsitu From submit LEFT JOIN City ON submit.Name = City.Name WHERE ID = ?'''
# lat = conn.execute(sql,x).fetchall()
# print(lat[2][0])
# print(len(lat))
#測試從submit和userID中抓取landsitu

# sql = '''select * From submit'''
# cities = conn.execute(sql).fetchall()
# print(cities)
# x = ("Hua","Taipei")
# sql = '''Delete From submit Where ID = ? And Name = ?'''
# conn.execute(sql,x)
# sql = '''select * From submit'''
# cities = conn.execute(sql).fetchall()
# print(cities)
#測試刪除table資料，移除訂閱
    
# test for fetch info

# conn.execute(sql,x)
conn.commit()
conn.close()