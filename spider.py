from selenium import webdriver
from selenium.webdriver.common.by import By
import sqlite3

class spider:
    def __init__(self,driverPath,options,url,db):
        self.driverPath = driverPath
        self.options = options
        self.url = url
        self.db = db
        # DRIVERPATH = 'C:\chromedriver-win64\chromedriver.exe'                                               #chromedriver path
        # headless = webdriver.ChromeOptions()
        # headless.add_argument('headless')                                                                   #隱藏操作
        # driver = webdriver.Chrome(options=headless)
    
    def get_db_connection(self):
        conn = sqlite3.connect(self.db)  #連線資料庫
        conn.row_factory = sqlite3.Row   #判定fetch成功與否
        return conn
    
    def scraping():
        print()