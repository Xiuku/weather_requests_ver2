from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import math

PATH = 'C:\chromedriver-win64\chromedriver.exe'
# headless = webdriver.ChromeOptions()
# headless.add_argument('headless')                                                                     #隱藏操作
driver = webdriver.Chrome()
driver.set_window_size(1280, 800)
print(driver.get_window_size())

cid = 10017
url = "https://www.cwa.gov.tw/V8/C/W/County/County.html?CID="                                             #天氣快照
edit = f"{url}{cid}"
# url = 'https://www.cwa.gov.tw/V8/C/W/County_WindTop.html'                                               #平均風速表
# driver.implicitly_wait(5)                                                                             #等待
driver.get(edit)


try:
    
    name = "高雄市"
    
    # select = driver.find_element(By.XPATH, "//select[@id='CID']").click()
    # citypath = f"//select[@id='CID']//option[@value='{cid}']"
    # city = driver.find_element(By.XPATH, citypath).click()

    nowtime = driver.find_element(By.XPATH, "//div[@class='d-xl-block d-none mb-3']//span").text
    print(nowtime)                  #時間

    weather = driver.find_element(By.XPATH, "//div[@class='col-lg-7']//li[1]//img[1]")
    cloudcover = ''
    print(weather.get_attribute('title'))
    
    match weather.get_attribute('title'):
        case s if "晴" in s:
            cloudcover = 'clear'
        case s if "雨" in s:
            cloudcover = 'rain'
        case s if "雲" in s or "陰" in s:
            cloudcover = 'cloudy'
        case _:
            cloudcover = 'unknown'
    print(cloudcover)
    
    rain = driver.find_element(By.XPATH, "//div[@class='col-lg-7']//li[1]//span[3]").text
    print(rain[5:])                 #total: 降雨機率\n{100}%

    temps = driver.find_elements(By.CLASS_NAME, "tem")
    #multiple \s and nowtime,tomorrow morning、evening and \s
    n_temp = [t.text for t in temps if t.text.strip()]

    print(n_temp[0])
    # min_temp = int(n_temp[0][:2])                                   #lowest temp
    # max_temp = int(n_temp[0][5:])                                   #highest temp
    # current_temp = round((min_temp + max_temp) / 2)
    # print(f"temp range: {n_temp[0]}")                               #total l_temp - h_temp
    # print(f"current temp: {current_temp}")
    # print(f"lowest temp: {min_temp}")
    # print(f"highest temp: {max_temp}")

    uv = driver.find_element(By.XPATH, "//tr[@id='ultra']//td[1]//strong[1]").text
    print(uv)

    # wind_ms = driver.find_elements(By.CLASS_NAME, "wind-MS")
    # # print(wind)
    # winds = [w.get_attribute("textContent") for w in wind_ms]
    # print(winds)
    # for w in wind_ms:
    #     print(w.get_attribute("textContent"))
    #取得風速:平時隱藏

    forecast_weather_get = driver.find_elements(By.XPATH, "//span[@class='signal']//img[1]")
    forecast_weather = [w.get_attribute('title') for w in forecast_weather_get]
    print(forecast_weather[1:6])
    forecast_temp_get = driver.find_elements(By.CLASS_NAME, "text-center")
    forecast_temp = [t.text for t in forecast_temp_get if t.text.strip()]
    print(forecast_temp[1:6])

    returns = []
    returns.append(forecast_weather[1:6])
    returns.append(forecast_temp[1:6])
    print(returns[0][1])
    #7-Day and night forecast(includes today), so we only need tomorrow and next 4-Days morning
    
    # time.sleep(10)

    # date = browser.find_element(By.XPATH, "//ul[@class='datetime']//span[@class='date']")
    # print(date.text)                                                                                  #work
    
except Exception as e:
    print("error")




# from s_quickInfo import snapshot
# from s_wind import wind

# PATH = 'C:\chromedriver-win64\chromedriver.exe'
# OPTION = 'headless'
# DB = "Weather.db"
# runs = snapshot(PATH,OPTION,"https://www.cwa.gov.tw/V8/C/W/County/County.html?CID=",DB)
# runtwo = wind(PATH,OPTION,'https://www.cwa.gov.tw/V8/C/W/County_WindTop.html',DB)

# conn = runs.get_db_connection()
# runs.scraping(conn=conn)
# runtwo.scraping(conn=conn)

# conn.close()