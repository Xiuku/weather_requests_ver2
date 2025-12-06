from selenium import webdriver
from selenium.webdriver.common.by import By
import sqlite3
import json
from datetime import datetime

from spider import spider

class snapshot(spider):
    def __init__(self,driverPath,options,url,db):
        self.driverPath = driverPath
        self.options = options
        self.url = url
        self.db = db
    
    def scraping(self,conn):
        workop = webdriver.ChromeOptions()
        workop.add_argument(self.options)

        driver = webdriver.Chrome(options=workop)
        driver.set_window_size(1280, 800)                                               #避免版面跑掉,資訊使用的樣式不同抓不到
        
        sql = '''select DISTINCT cID From City Order by cID ASC'''
        cid = conn.execute(sql).fetchall()

        for c in cid:
            edit = f"{self.url}{c[0]}"
            driver.get(edit)
            
            temps = driver.find_elements(By.CLASS_NAME, "tem")                          #tem儲存位置
            n_temp = [t.text for t in temps if t.text.strip()]                          #取得current、2nd time section、3rd
            current_temp = n_temp[0]

            rain = driver.find_element(By.XPATH, "//div[@class='col-lg-7']//li[1]//span[3]").text           #取得current rain%
            rainfall = rain[5:]                                                         #String: "降雨機率" + "\n" + "{100}%"

            uv = driver.find_element(By.XPATH, "//tr[@id='ultra']//td[1]//strong[1]").text                  #取得uv

            weather = driver.find_element(By.XPATH, "//div[@class='col-lg-7']//li[1]//img[1]")              #取得天氣
            cloudcover = ""

            match weather.get_attribute('title'):
                case s if "晴" in s:
                    cloudcover = 'clear'
                case s if "雨" in s:
                    cloudcover = 'rain'
                case s if "雲" in s:
                    cloudcover = 'clouds'
                case s if "陰" in s:
                    cloudcover = 'mist'
                case _:
                    cloudcover = 'unknown'

            info = (current_temp,rainfall,uv,cloudcover,c[0])
            toDB = '''UPDATE weather SET temp = ?,rainfall = ?,uv = ?,cloudcover = ? Where cid = ?'''
            conn.execute(toDB,info)
            
        conn.commit()

    def forecast(self,cid):
        workop = webdriver.ChromeOptions()
        workop.add_argument(self.options)   #set options

        driver = webdriver.Chrome(options=workop)
        driver.set_window_size(1280, 800)   #set driver

        edit = f"{self.url}{cid}"
        driver.get(edit)

        forecast_weather_get = driver.find_elements(By.XPATH, "//span[@class='signal']//img[1]")
        forecast_weather = [w.get_attribute('title') for w in forecast_weather_get]
        forecast_temp_get = driver.find_elements(By.CLASS_NAME, "text-center")
        forecast_temp = [t.text for t in forecast_temp_get if t.text.strip()]
        #7-Day and night forecast(includes today), because we doing 5-Day forecast, so we only need tomorrow and next 4-Days morning
        forecast = []
        forecast.append(forecast_weather[:5])
        forecast.append(forecast_temp[:5])
        return forecast




        