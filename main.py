import datetime
import string
from flask import Flask, render_template, request, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
import os
from dotenv import load_dotenv
import sqlite3
from sendMail import s_Mail

from s_quickInfo import snapshot
from s_wind import wind

PATH = 'C:\chromedriver-win64\chromedriver.exe'
OPTION = 'headless'
DB = "Weather.db"
MAIL_USER = "Yours email"
MAIL_PASSWORD = "emali app password"

tem_init = snapshot(PATH,OPTION,"https://www.cwa.gov.tw/V8/C/W/County/County.html?CID=",DB)
wind_init = wind(PATH,OPTION,'https://www.cwa.gov.tw/V8/C/W/County_WindTop.html',DB)
mailer = s_Mail(MAIL_USER, MAIL_PASSWORD)

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DB)          #連線資料庫
    conn.row_factory = sqlite3.Row      #checkout fetch is work or not
    return conn

def scheduled_job():
    # print(f"[{datetime.datetime.now()}] 開始執行每日天氣更新與寄信任務...")
    
    conn = get_db_connection()
    
    try:
        # print("正在更新天氣資料...")
        tem_init.scraping(conn=conn)
        wind_init.scraping(conn=conn)
        
        # 更新資料庫中的日期顯示
        weekday = datetime.datetime.now().strftime("%A")
        today = datetime.datetime.now()
        date_str = f"{today.month}/{today.day}"
        tem_init.getDate(conn, weekday, date_str)
        
        users_sql = '''SELECT ID, email FROM User'''
        users = conn.execute(users_sql).fetchall()
        
        for user in users:
            uid = user['ID']
            u_email = user['email']
            # print(f"正在寄送給: {uid} ({u_email})")
            mailer.send_daily_digest(uid, u_email)
            
        print("所有郵件發送完畢。")
        
    except Exception as e:
        print(f"排程任務發生錯誤: {e}")
    finally:
        conn.close()

# 取得正常執行狀態時，在特定時間發送郵件
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=scheduled_job, trigger="cron", hour=6, minute=0)
    scheduler.start()

user_id = ""                              #保存當前登入使用者ID

# Display home page and get city name entered into search form
# 顯示主頁面，並且取得城市名輸入進搜尋欄
# @app. is the flask units.When lead to the route(/......) runs the def content
@app.route("/", methods=["GET", "POST"])
def home():
    global tem_init
    global wind_init
    
    conn = tem_init.get_db_connection()
    try:
        getlatest = '''select * From time Order By timestamp DESC'''
        latest = conn.execute(getlatest).fetchone()                     #取得資料庫最新的天氣更新時間
        today = datetime.datetime.now()
        date = f"{today.month}/{today.day}"
        if latest is None or latest['date'] != date:                    # if 時間對不上最新時間
            weekday = datetime.datetime.now().strftime("%A")            # 取得weekday
            tem_init.scraping(conn=conn)                                # 抓取最新資料
            wind_init.scraping(conn=conn)
            tem_init.getDate(conn,weekday,date)                         # 加入最新時間
    finally:
        conn.close()                                                # 關閉資料庫
        # print("getting data")
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
    global tem_init
    global wind_init
    city_name = string.capwords(city)                               #capwords回傳 字串:首字母大寫,其餘小寫
    today = datetime.datetime.now()                                 #returns yyyy-mm-dd hh:mm:ss
    current_date = today.strftime("%A, %B %d")                      #Full-Weekday,Full-months(name),day/months
    conn = tem_init.get_db_connection()                             #資料庫連接

    x = (city_name,)
    sql = '''Select cID from City where name = ?'''
    cid = conn.execute(sql,x).fetchone()
    if cid is None:
        return redirect(url_for("error"))
    else:
        cid = cid[0]
    #原透過城市名稱取得地理location,以loc取得weatherAPI.並相相關loc存入DB
    #現透過cid、cityname取得城市天氣頁面,在頁面進行爬蟲取得所有的天氣資料

    x = (cid,)
    sql = '''select * From weather Where cid = ?'''
    weather = conn.execute(sql,x).fetchall()
    # for w in weather:
    #     print(w['temp'],w['rainfall'],w['cloudcover'],w['uv'],w['windspeed'])

    for w in weather:
        #data likes {Low-temp - high-temp}
        min_temp = int(w['temp'][:2])                                   #lowest temp
        max_temp = int(w['temp'][5:])                                   #highest temp
        current_temp = round((min_temp + max_temp) / 2)                 #current temperature
        
        current_weather = w['cloudcover']
        wind_speed = w['windspeed']                                     #wind speeds
        rain = w['rainfall']
        uv = w['uv']
    # Get current weather data
    # 取得當前氣象資料

    # Get five-day weather forecast data
    # 取得未來五天天氣預報資料
    forecast = tem_init.forecast(cid)
    
    # Make lists of temperature and weather description data to show user
    # 讓氣溫和天氣描述資料的list顯示給使用者
    five_day_temp_list = [temp for temp in forecast[1]]
    # 在五天預報內中的正午12點,取得相關溫度
    five_day_weather_list = []
    for s in forecast[0]:
        match s:
            case s if "晴" in s:
                five_day_weather_list.append('clear')
            case s if "雨" in s:
                five_day_weather_list.append('rain')
            case s if "雲" in s:
                five_day_weather_list.append('clouds')
            case s if "陰" in s:
                five_day_weather_list.append('mist')
            case _:
                five_day_weather_list.append('unknown')
    # 在五天預報內中的正午12點,取得相關氣象

    # Get next four weekdays to show user alongside weather data
    # 取得接下來四個工作天給使用者
    five_day_unformatted = [today + datetime.timedelta(days=1), today + datetime.timedelta(days=2),today + datetime.timedelta(days=3),
                            today + datetime.timedelta(days=4), today + datetime.timedelta(days=5)]
    five_day_dates_list = [date.strftime("%a") for date in five_day_unformatted]

    if request.method == "POST":
        action = request.form.get("action")                             #表單回傳
        if action == "sub":                                             #使用者按下 "+" 按鈕
                try:
                    z = (user_id,city_name)                             #抓取城市
                    sql =  '''INSERT INTO submit VALUES(?,?)'''         #以使用者ID,城市名稱，登入至資料庫中兩者連接內容
                    conn.execute(sql,z)
                    conn.commit()
                except sqlite3.IntegrityError:                          #錯誤:唯一性。
                    message = "此城市已經登記過"
                    print(message)#test
                finally:
                    conn.close()
                    return redirect(url_for("sub_city"))                #關閉資料庫，並跳轉至登記城市頁面

    return render_template("city.html", city_name=city_name, current_date=current_date, current_temp=current_temp,
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
    sub_sql = '''Select submit.Name, City.cID From submit LEFT JOIN City ON submit.Name = City.Name WHERE ID = ?'''
    cids = conn.execute(sub_sql,x).fetchall()
    
    try:
        for row in cids:                                                #循環存取,一個個拜訪訂閱的城市
            city_name = row[0]
            cid = row[1]

            cache_sql = '''SELECT * From weather WHERE cid = ?'''
            cached_data = conn.execute(cache_sql,(cid,)).fetchone()     #取得第i個拜訪的城市天氣資料

            weather_info = {}
            if cached_data:
                weather_info = {
                    "name" : city_name,
                    "temp" : cached_data['temp'],
                    "weather" : cached_data['cloudcover'],
                }
            else:
                weather_info = {"name":city_name, "temp":"N/A", "weather":"Error"}
            cities.append(weather_info)                                 #增添至頁面快訊
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

