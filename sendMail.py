import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
import re

class s_Mail:
    def __init__(self, sender, app_password, db_path="Weather.db"):
        self.sender = sender
        self.app_ps = app_password
        self.db_path = db_path
        
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _analyze_weather(self, temp_str, rainfall_str, wind_speed, uv, cloud_cover):
        analysis = []

        #溫度分析
        try:
            temps = re.findall(r'\d+', temp_str) # 抓取字串中所有數字
            if len(temps) >= 2:
                avg_temp = (int(temps[0]) + int(temps[1])) / 2
            else:
                avg_temp = int(temps[0])

            if avg_temp < 15:
                analysis.append(f"🥶 氣溫偏低 (約{avg_temp}°C)，請務必穿著保暖外套。")
            elif 15 <= avg_temp < 24:
                analysis.append(f"😊 氣候舒適 (約{avg_temp}°C)，適合外出活動。")
            elif 24 <= avg_temp < 30:
                analysis.append(f"😎 天氣溫暖 (約{avg_temp}°C)，體感舒適。")
            else:
                analysis.append(f"🥵 天氣炎熱 (約{avg_temp}°C)，請注意防曬與補水。")
        except:
            analysis.append(f"氣溫資料 ({temp_str})。")

        #降雨與天氣狀態分析
        rain_prob = 0
        try:
            rain_prob = int(re.sub(r'\D', '', rainfall_str)) # 去除 % 取數字
        except:
            pass

        if rain_prob >= 50 or "雨" in cloud_cover:
            analysis.append(f"☔ 下雨機率高 ({rainfall_str})，出門請記得帶傘。")
        elif rain_prob >= 30:
            analysis.append(f"☁️ 稍微陰沉 ({rainfall_str} 降雨率)，建議攜帶雨具備用。")
        else:
            if uv >= 7:
                analysis.append(f"☀️ 晴朗但紫外線強 (UV: {uv})，請注意防曬。")
            else:
                analysis.append(f"🌤️ 天氣穩定，降雨機率低。")

        #風速分析
        try:
            wind = float(wind_speed)
            if wind > 10:
                analysis.append("💨 風勢強勁，騎車或行走請注意安全。")
            elif wind > 5:
                analysis.append("🍃 有明顯微風，體感會稍涼。")
        except:
            pass

        return " ".join(analysis)

    def send_daily_digest(self, user_id, to_email):
        conn = self.get_db_connection()
        
        # (Join): 取得 使用者訂閱 -> 城市ID -> 天氣資料
        sql = '''
        SELECT City.Name, weather.temp, weather.rainfall, weather.cloudcover, weather.windspeed, weather.UV 
        FROM submit 
        JOIN City ON submit.Name = City.Name 
        JOIN weather ON City.cID = weather.cID 
        WHERE submit.ID = ?
        '''
        rows = conn.execute(sql, (user_id,)).fetchall()
        conn.close()

        if not rows:
            print(f"User {user_id} has no subscriptions.")
            return

        # 建構 HTML 郵件內容
        html_body = "<html><body>"
        html_body += "<h2 style='color: #2c3e50;'>今日天氣日報 WeatherInfo</h2>"
        html_body += "<hr style='border: 1px solid #eee;'>"

        for row in rows:
            city_name = row['Name']
            # 獲取分析建議
            advice = self._analyze_weather(
                row['temp'], row['rainfall'], row['windspeed'], row['UV'], row['cloudcover']
            )
            # 原始資料字串
            raw_data = f"Temp: {row['temp']}°C | Rain: {row['rainfall']} | Wind: {row['windspeed']}m/s | UV: {row['UV']} | Status: {row['cloudcover']}"

            # 大標題(城市)、中字體(分析)、小字體(資料)
            html_body += f"""
            <div style='margin-bottom: 25px; font-family: sans-serif;'>
                <h1 style='font-size: 30px; color: #333; margin-bottom: 5px;'>{city_name}</h1>
                <p style='font-size: 18px; color: #2980b9; font-weight: bold; margin: 5px 0;'>
                    {advice}
                </p>
                <p style='font-size: 12px; color: #7f8c8d; background-color: #f9f9f9; padding: 5px; border-radius: 4px;'>
                    詳細資料: {raw_data}
                </p>
                <hr style='border: 0; border-top: 1px dashed #ccc; margin-top: 15px;'>
            </div>
            """
        
        html_body += "<p style='text-align: center; color: #aaa;'>End of Report</p></body></html>"

        # 發送郵件
        msg = MIMEMultipart()
        msg["From"] = self.sender
        msg["To"] = to_email
        msg["Subject"] = "WeatherInfo: 您的每日天氣分析報告"

        # 設定為 HTML 格式
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.sender, self.app_ps)
                server.send_message(msg)
                print(f"Weather digest sent successfully to {to_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")