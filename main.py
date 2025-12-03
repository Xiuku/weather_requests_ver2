import datetime
import requests
import string
from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
import math
import sqlite3
import json
load_dotenv()
#讀取API_KEY saves in .env

OWM_ENDPOINT = "https://pro.openweathermap.org/data/2.5/weather"
OWM_FORECAST_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"
GEOCODING_API_ENDPOINT = "http://api.openweathermap.org/geo/1.0/direct"
api_key = os.getenv("OWM_API_KEY")
# api_key = os.environ.get("OWM_API_KEY")

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("Weather.db")  #連線資料庫
    conn.row_factory = sqlite3.Row
    return conn

user_id = ""                              #保存當前登入使用者ID

# Display home page and get city name entered into search form
# 顯示主頁面，並且取得城市名輸入進搜尋欄
# @app. is the flask units.When lead to the route(/......) runs the def content
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        city = request.form.get("search")
        return redirect(url_for("get_weather", city=city))          #一直等待,直到使用者輸入後重新導向至city.html + cityname
    return render_template("index.html")                            #沒有輸入,導向至home()時開啟index.html(首頁)

@app.route("/users", methods=["GET", "POST"])
def userInfo():
    message = ""        #回傳給html的提示
    is_error = False    #會用來控制 placeholder 顏色
    global user_id

    if request.method == "POST":
        id = request.form.get("id")
        mail = request.form.get("mail")
        x = (id,mail)

        action = request.form.get("action")  # "login" 或 "signup"

        conn = get_db_connection()           #連線資料庫

        if action == "signup":               #表單回傳，如果是註冊
            try:
                sql =  '''INSERT INTO user VALUES(?,?)'''           #資料庫中新增內容
                conn.execute(sql,x)
                conn.commit()
                message = "註冊成功"
            except sqlite3.IntegrityError:                          #錯誤:唯一性
                message = "此ID或email已經註冊過"                        #遇到同樣email
                is_error = True
            except TypeError:
                message = "請重新輸入並確認非法字元"                  #不可被接受字元:ID、email輸入內容
                is_error = True

        elif action == "login":              #表單回傳，如果是登入
            sql =  '''Select * From user WHERE id = ? AND email = ?'''      #選擇表單和資料庫中同樣的內容
            result = conn.execute(sql,x).fetchone()                         #提取

            if result:
                message = "登入成功"                                         #提取成功
                getID = '''Select ID From user WHERE id = ? AND email = ?'''#取得ID
                user_id = conn.execute(getID,x).fetchone()[0]
                return redirect(url_for("sub_city",user_id=user_id))        #重新導向至已訂閱城市頁面，以輸入者的ID登入
            else:
                message = "沒有帳號，請註冊!"                                #提取失敗，告知需註冊
                is_error = True

        conn.close()

    return render_template("user.html", message=message, is_error=is_error)


# Display weather forecast for specific city using data from OpenWeather API
# 為特定城市顯示氣象預報,資料來源於OpenWeather API
@app.route("/<city>", methods=["GET", "POST"])
def get_weather(city):
    # Format city name and get current date to display on page
    # 設定城市名稱格式並取得現有資料顯示於頁面
    global user_id
    city_name = string.capwords(city)                               #capwords回傳 字串:首字母大寫,其餘小寫
    today = datetime.datetime.now()                                 #returns yyyy-mm-dd hh:mm:ss
    current_date = today.strftime("%A, %B %d")                      #Full-Weekday,Full-months(name),day/months
    conn = get_db_connection()                                      #資料庫連接

    # Get latitude and longitude for city
    # 取得城市經緯度
    location_params = {
        "q": city_name,
        "appid": api_key,
        "limit": 3,
    }

    x = (city_name,)
    sql = '''Select Landsitu From City Where Name = ?'''
    getloc = conn.execute(sql,x).fetchone()                         #查詢資料庫中是否有城市地理編碼
    if getloc is None:
        #取得地理編碼
        location_response = requests.get(GEOCODING_API_ENDPOINT, params=location_params)
        # http://api.openweathermap.org/geo/1.0/direct?q={city name},limit={limit}&appid={API key}
        location_data = location_response.json()
        # returns a list,so every things in [0].in the other words [{key : values}.dict the json looks like].list
    
        # Prevent IndexError if user entered a city name with no coordinates by redirecting to error page
        # 預防索引錯誤.如果城市名稱沒有座標導致導向錯誤頁面
        if not location_data:
            return redirect(url_for("error"))
        else:
            lat = location_data[0]['lat']
            lon = location_data[0]['lon']
            country = location_data[0]['country']
            y1 = (city_name, f"[{lat},{lon}]")                  #保存CityName和地理座標
            sql = '''INSERT INTO City (Name, Landsitu) VALUES(?,?)'''
            conn.execute(sql,y1)
            y2 = (city_name, country)
            sql = '''INSERT INTO Area (Name, area) VALUES(?,?)'''
            conn.execute(sql,y2)
            conn.commit()
    else:
        getloc = json.loads(getloc[0])
        lat = getloc[0]
        lon = getloc[1]                                                   #資料庫載入
        sql = '''Select area From Area Where Name = ?'''
        country = conn.execute(sql,x).fetchone()[0]


    # Get OpenWeather API data
    # 取得OpenWeather API
    weather_params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
    }
    weather_response = requests.get(OWM_ENDPOINT, weather_params)
    weather_response.raise_for_status()                             #回傳HTTP狀態碼,user's error = 4xx, server's error = 5xx,normal in 200-299
    weather_data = weather_response.json()

    # Get current weather data
    # 取得當前氣象資料
    current_temp = round(weather_data['main']['temp'])              #current temperature
    current_weather = weather_data['weather'][0]['main']            #now the weather looks like
    min_temp = math.floor(weather_data['main']['temp_min'])         #lowest temp
    max_temp = math.ceil(weather_data['main']['temp_max'])          #highest temp
    wind_speed = weather_data['wind']['speed']                      #wind speeds

    # Get five-day weather forecast data
    # 取得未來五天天氣預報資料
    forecast_response = requests.get(OWM_FORECAST_ENDPOINT, weather_params)
    forecast_data = forecast_response.json()

    # Make lists of temperature and weather description data to show user
    # 讓氣溫和天氣描述資料的list顯示給使用者
    five_day_temp_list = [round(item['main']['temp']) for item in forecast_data['list'] if '12:00:00' in item['dt_txt']]
    # 在五天預報內中的正午12點,取得相關溫度
    five_day_weather_list = [item['weather'][0]['main'] for item in forecast_data['list'] if '12:00:00' in item['dt_txt']]
    # 在五天預報內中的正午12點,取得相關氣象

    # Get next four weekdays to show user alongside weather data
    # 取得接下來四個工作天給使用者
    five_day_unformatted = [today, today + datetime.timedelta(days=1), today + datetime.timedelta(days=2),
                            today + datetime.timedelta(days=3), today + datetime.timedelta(days=4)]
    five_day_dates_list = [date.strftime("%a") for date in five_day_unformatted]

    if request.method == "POST":
        action = request.form.get("action")                             #表單回傳
        if action == "sub":                                             #使用者按下 "+" 按鈕
                try:
                    z = (user_id,city_name)                             #抓取城市
                    sql =  '''INSERT INTO submit VALUES(?,?)'''         #以使用者ID,城市名稱，登入至資料庫中兩者連接內容
                    conn.execute(sql,z)
                    conn.commit()
                except sqlite3.IntegrityError:                          #錯誤:唯一性，資料庫使用取代。錯誤不會發生
                    message = "此城市已經登記過"
                    print(message)#test
                finally:
                    conn.close()
                    return redirect(url_for("sub_city"))                #關閉資料庫，並跳轉至登記城市頁面

    return render_template("city.html", city_name=city_name, current_date=current_date, country = country, current_temp=current_temp,
                           current_weather=current_weather, min_temp=min_temp, max_temp=max_temp, wind_speed=wind_speed,
                           five_day_temp_list=five_day_temp_list, five_day_weather_list=five_day_weather_list,
                           five_day_dates_list=five_day_dates_list)


@app.route("/s_city", methods=["GET", "POST"])
def sub_city():
    global user_id
    cities = []
    # DataFormat : {"name": string, "temp": int, "icon_url": png.route},
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()                                          #連線資料庫
    x = (user_id,)                                                      #選擇登入者的ID
    sub_sql = '''Select submit.Name, City.Landsitu From submit LEFT JOIN City ON submit.Name = City.Name WHERE ID = ?'''
    getloc = conn.execute(sub_sql,x).fetchall()

    try:
        for row in getloc:
            city_name = row[0]
            landsitu_json = row[1]

            cache_sql = '''SELECT temperature,cloudcover,Lastupdated From weather WHERE Name = ?'''
            cached_data = conn.execute(cache_sql,(city_name,)).fetchone()

            weather_info = {}
            if cached_data and cached_data[2] == today_str:
                weather_info = {
                    "name" : city_name,
                    "temp" : cached_data[0],
                    "weather" : cached_data[1],
                }
            else:
                if landsitu_json:
                    jsonloc = json.loads(landsitu_json)
                    lat = jsonloc[0]
                    lon = jsonloc[1]

                    weather_params = {
                        "lat": lat,
                        "lon": lon,
                        "appid": api_key,
                        "units": "metric",
                    }
                    try:                                                #當user初登入時\每天首次登入時，進入訂閱城市取得每個城市當天的天氣狀況
                        weather_response = requests.get(OWM_ENDPOINT, weather_params)
                        weather_response.raise_for_status()
                        weather_data = weather_response.json()

                        temp = round(weather_data['main']['temp'])                      #temperature
                        weather = weather_data['weather'][0]['main']                    #the weather looks like

                        x = (city_name, temp, weather, today_str)
                        upsert_sql = '''INSERT OR REPLACE INTO weather (Name, temperature, cloudcover, Lastupdated) VALUES(?, ?, ?, ?)'''
                        conn.execute(upsert_sql,x)
                        conn.commit()
                        weather_info = {
                            "name" : city_name,
                            "temp" : temp,
                            "weather" : weather,
                        }
                    except Exception as e:
                        weather_info = {"name":city_name, "temp":"N/A", "weather":"Error"}
                else:
                    weather_info = {"name":city_name, "temp":"N/A", "weather":"Error"}
            cities.append(weather_info)                                                 #增添至頁面快訊
    finally:
        pass

    if request.method == "POST":
        d_city = request.form.get("action")
        try:
            x = (user_id,d_city)
            sql = '''Delete From submit Where ID = ? And Name = ?'''
            conn.execute(sql,x)                                         #delete the city from submit
            conn.commit()
        except Exception as e:
            print(e)
        finally:
            conn.close()
            return redirect(url_for("sub_city"))

    #修正資料庫使其能夠抓取天氣資料
    return render_template("s_city.html",user_id = user_id,cities=cities)

# Display error page for invalid input
# 對於無效輸入顯示錯誤頁面
@app.route("/error")
def error():
    return render_template("error.html")


if __name__ == "__main__":
    app.run(debug=True)
