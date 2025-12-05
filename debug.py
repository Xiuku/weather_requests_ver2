import datetime
import requests
import string
from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
import json
load_dotenv()
#讀取API_KEY saves in .env

OWM_ENDPOINT = "https://pro.openweathermap.org/data/2.5/weather"
OWM_FORECAST_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"
GEOCODING_API_ENDPOINT = "http://api.openweathermap.org/geo/1.0/direct"
api_key = os.getenv("OWM_API_KEY")
# api_key = os.environ.get("OWM_API_KEY")

# app = Flask(__name__)

# Display home page and get city name entered into search form
# 顯示主頁面，並且取得城市名輸入進搜尋欄
# @app. is the flask units.When lead to the route(/......) runs the def content
# @app.route("/",methods=["GET","POST"])
def home():
    # if request.method == "POST":
    #     city = request.form.get("search")
    #     return redirect(url_for("get_weather", city=city))
    city = input("請輸入查詢城市:")
    return city
    # return render_template("index.html")

# @app.route("/users")
def userInfo():
    return render_template("user.html")

# Display weather forecast for specific city using data from OpenWeather API
# 為特定城市顯示氣象預報,資料來源於OpenWeather API
# @app.route("/<city>", methods=["GET", "POST"])
def get_weather(city):
    # Format city name and get current date to display on page
    # 設定城市名稱格式並取得現有資料顯示於頁面
    city_name = string.capwords(city)                               #capwords回傳 字串:首字母大寫,其餘小寫
    today = datetime.datetime.now()                                 #returns yyyy-mm-dd hh:mm:ss
    current_date = today.strftime("%A, %B %d")                      #Full-Weekday,Full-months(name),day/months

    # Get latitude and longitude for city
    # 取得城市經緯度
    location_params = {
        "q": city_name,
        "limit": 3,
        "appid": api_key,
    }

    location_response = requests.get(GEOCODING_API_ENDPOINT, params=location_params)
    # http://api.openweathermap.org/geo/1.0/direct?q={city name},limit={limit}&appid={API key}
    location_data = location_response.json()
    # loc_data_json = json.dumps(location_data)
    # print(type(loc_data_json),loc_data_json)
    
    # Prevent IndexError if user entered a city name with no coordinates by redirecting to error page
    # 預防索引錯誤.如果城市名稱沒有座標導致導向錯誤頁面
    if not location_data:
        print("no data")
    else:
        lat = location_data[0]['lat']
        lon = location_data[0]['lon']

    # Get OpenWeather API data
    # 取得OpenWeather API
    weather_params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
    }
    weather_response = requests.get(OWM_ENDPOINT, weather_params)
    weather_response.raise_for_status()
    weather_data = weather_response.json()
    # weather_json = json.dumps(weather_data)
    # print(weather_json)

    # Get current weather data
    # 取得當前氣象資料
    current_temp = round(weather_data['main']['temp'])
    current_weather = weather_data['weather'][0]['main']
    min_temp = round(weather_data['main']['temp_min'])
    max_temp = round(weather_data['main']['temp_max'])
    wind_speed = weather_data['wind']['speed']

    # Get five-day weather forecast data
    # 取得未來五天天氣預報資料
    forecast_response = requests.get(OWM_FORECAST_ENDPOINT, weather_params)
    forecast_data = forecast_response.json()
    # forecast_json = json.dumps(forecast_data)
    # print(forecast_json)

    # Make lists of temperature and weather description data to show user
    # 讓氣溫和天氣描述資料的list顯示給使用者
    five_day_temp_list = [round(item['main']['temp']) for item in forecast_data['list'] if '12:00:00' in item['dt_txt']]
    five_day_weather_list = [item['weather'][0]['main'] for item in forecast_data['list'] if '12:00:00' in item['dt_txt']]

    # Get next four weekdays to show user alongside weather data
    # 取得接下來四個工作天給使用者
    five_day_unformatted = [today, today + datetime.timedelta(days=1), today + datetime.timedelta(days=2),
                            today + datetime.timedelta(days=3), today + datetime.timedelta(days=4)]
    five_day_dates_list = [date.strftime("%a") for date in five_day_unformatted]

    info = [city_name,current_date,current_temp,current_weather,min_temp,max_temp,wind_speed,five_day_temp_list,five_day_weather_list,five_day_dates_list]

    return info
    # return render_template("city.html", city_name=city_name, current_date=current_date, current_temp=current_temp,
    #                        current_weather=current_weather, min_temp=min_temp, max_temp=max_temp, wind_speed=wind_speed,
    #                        five_day_temp_list=five_day_temp_list, five_day_weather_list=five_day_weather_list,
    #                        five_day_dates_list=five_day_dates_list)


# Display error page for invalid input
# 對於無效輸入顯示錯誤頁面
# @app.route("/error")
def error():
    return render_template("error.html")


if __name__ == "__main__":
    # city = home()
    # print(city)
    weather = get_weather(city="Taipei")
    print(weather)
    # app.run(debug=True)
