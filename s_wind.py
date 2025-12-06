from selenium import webdriver
from selenium.webdriver.common.by import By
import sqlite3
import json
from datetime import datetime

from spider import spider

class wind(spider):
    def __init__(self,driverPath,options,url,db):
        self.driverPath = driverPath
        self.options = options
        self.url = url
        self.db = db
    
    def scraping(self,conn):
        workop = webdriver.ChromeOptions()
        workop.add_argument(self.options)

        driver = webdriver.Chrome(options=workop)
        driver.set_window_size(945, 1020)                                               #避免版面跑掉,資訊使用的樣式不同抓不到
        driver.get(self.url)

        wind_ms = driver.find_elements(By.CLASS_NAME, "wind-MS")
        winds = [w.get_attribute("textContent") for w in wind_ms]

        c = [10017,63,65,68,10018,10004,10005,66,10007,10008,10009,10020,10010,67,64,10013,10002,10015,10014,10016,9020,9007]
        
        for i in range(len(winds)):
            info = (winds[i],c[i])
            toDB = '''UPDATE weather SET windspeed = ? Where cid = ?'''
            conn.execute(toDB,info)
        conn.commit()




        