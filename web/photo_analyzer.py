
import exifread
import requests
import googlemaps
from datetime import datetime
from config import Config
from pytz import timezone
from tidegraph import create_tide_graph
from flask import session
import base64
import os
import shutil

gmaps = googlemaps.Client(key=Config.GOOGLE_MAPS_API_KEY)
WEATHER_API_KEY = Config.OPENWEATHER_API_KEY

def get_location(lat, lon):
    result = gmaps.reverse_geocode((lat, lon))
    return result[0]['formatted_address']

def get_weather(lat, lon, dt):
    date_string = dt.strftime('%Y-%m-%d')
    url = f'http://api.weatherapi.com/v1/history.json?key={WEATHER_API_KEY}&q={lat},{lon}&dt={date_string}'
    response = requests.get(url)
    data = response.json()
    return data


def get_static_map_image(latitude, longitude):
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={latitude},{longitude}&zoom=15&size=600x400&markers=color:red%7C{latitude},{longitude}&key={Config.GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    return response.content

def get_wind_direction_str(degrees):
    if 337.5 < degrees <= 360 or 0 <= degrees <= 22.5:
        return "北"
    elif 22.5 < degrees <= 67.5:
        return "北東"
    elif 67.5 < degrees <= 112.5:
        return "東"
    elif 112.5 < degrees <= 157.5:
        return "南東"
    elif 157.5 < degrees <= 202.5:
        return "南"
    elif 202.5 < degrees <= 247.5:
        return "南西"
    elif 247.5 < degrees <= 292.5:
        return "西"
    else:
        return "北西"
import requests
import json

def getFishName(img):

    # 写真をGoogle Cloud Vision APIに送信します。
    url = "https://vision.googleapis.com/v1/images:annotate?key=YOUR_API_KEY"
    data = {
    "requests": [
      {
        "image": {
          "content": photo
        },
        "features": [
          {
            "type": "LABEL_DETECTION",
            "maxResults": 1
          }
        ]
      }
    ]
    }

    response = requests.post(url, data=json.dumps(imh))
    annotations = response.json()["responses"][0]["labelAnnotations"]
    fishname=""
    # 結果をユーザーに返します。
    if annotations:
        fishname="これは魚です！魚の名前は " + annotations[0]["description"] + " です。"

    return fishname



def analyze_photo():


    image_save_path = os.path.join(session['temp_folder'], session['img_file'])

    with open(image_save_path, 'rb') as f:
        tags = exifread.process_file(f)

    if 'GPS GPSLatitude' not in tags or 'GPS GPSLongitude' not in tags or 'EXIF DateTimeOriginal' not in tags:
        return #{'error':'画像から位置情報が取得出来ません'}

    lat = tags['GPS GPSLatitude'].values
    lon = tags['GPS GPSLongitude'].values
    lat = float(lat[0]) + float(lat[1]) / 60 + float(lat[2]) / 3600
    lon = float(lon[0]) + float(lon[1]) / 60 + float(lon[2]) / 3600
    if tags['GPS GPSLatitudeRef'].values == 'S':
        lat = -lat
    if tags['GPS GPSLongitudeRef'].values == 'W':
        lon = -lon

    location = get_location(lat, lon)
    # Googleマップ画像を取得し、ファイルとして保存
    map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=18&size=600x300&maptype=roadmap&markers=color:red%7C{lat},{lon}&key={Config.GOOGLE_MAPS_API_KEY}"
    map_image = requests.get(map_url).content
    map_image_name = f"map_{datetime.now().timestamp()}.png"
    map_image_path = f"{str(session['temp_folder'])}/{map_image_name}"

    with open(map_image_path, 'wb') as map_file:
        map_file.write(map_image)


    date_time = datetime.strptime(str(tags['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S')
    date_time = date_time.replace(tzinfo=timezone('UTC'))

    tide_img=create_tide_graph(date_time,date_time.hour,lat,lon)

    weather_data = get_weather(lat, lon, date_time)


    weather = weather_data['forecast']['forecastday'][0]['day']['condition']['text']
    temperature = weather_data['forecast']['forecastday'][0]['day']['avgtemp_c']
    hourly_data = weather_data['forecast']['forecastday'][0]['hour'][int(date_time.hour)]

    wind_speed_kph = hourly_data['wind_kph']
    wind_speed_ms = round(wind_speed_kph * 1000 / 3600, 1)
    wind_direction_deg = hourly_data['wind_degree']
    wind_direction_str = get_wind_direction_str(wind_direction_deg)

    return {
        'location': location,
        'map_point':map_image_name,
        'date_time': date_time,
        'weather': weather,
        'temperature': temperature,
        'wind_speed': wind_speed_ms,
        'wind_direction': wind_direction_str,
        'image_path': session['img_file'],
        'tide_path': tide_img
    }
