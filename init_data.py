import requests
from bs4 import BeautifulSoup
import sqlite3

# データベースの接続とテーブルの作成
conn = sqlite3.connect("db/tide_data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tide_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    point_code TEXT,
    latitude TEXT,
    longitude TEXT,
    date TEXT,
    hour INTEGER,
    tide_level INTEGER
)
""")

# 指定されたポイントの情報
points_info = {
    "Z1": {"latitude": "35°10'", "longitude": "139°37'"},
    "QN": {"latitude": "35°17'", "longitude": "139°39'"},
    "HM": {"latitude": "35°26'", "longitude": "139°40'"}
}

# 指定されたポイントのデータを取得してデータベースに保存する関数
def fetch_and_save_tide_data(point_code,year):
    url = f"https://www.data.jma.go.jp/kaiyou/data/db/tide/suisan/txt/{year}/{point_code}.txt"
    print(url)
    response = requests.get(url)
    data = response.text

    lines = data.split("\n")
    for line in lines[1:]:
        if not line.strip():
            continue
        date = line[72:78].strip()
        point = line[78:80].strip()


        for hour, column in enumerate(range(0, 72, 3)):

            tide_level = int(line[column:column + 3].strip())

            if tide_level != 999:
                cursor.execute("""
                INSERT INTO tide_data (point_code, latitude, longitude, date, hour, tide_level)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (point_code, points_info[point_code]["latitude"], points_info[point_code]["longitude"], date.replace(" ", "0"), hour, tide_level))

    conn.commit()

# 各ポイントのデータを取得してデータベースに保存
for point_code in points_info.keys():
    fetch_and_save_tide_data(point_code,2023)
    fetch_and_save_tide_data(point_code,2022)


# データベースの接続を閉じる
conn.close()
