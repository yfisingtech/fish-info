import sqlite3
import datetime
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib
from flask import session
matplotlib.use("Agg")


def get_tide_data(date, hour, latitude, longitude):
    target_datetime = date
    start_datetime = target_datetime - datetime.timedelta(hours=12)
    end_datetime = target_datetime + datetime.timedelta(hours=12)
    print(start_datetime.strftime("%y%m%d%H"))
    print(end_datetime.strftime("%y%m%d%H"))
    conn = sqlite3.connect("../db/tide_data.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT date, hour, latitude, longitude, tide_level
    FROM tide_data
    WHERE date || hour >= ? AND date || hour <= ? order by date,hour asc
    """, (start_datetime.strftime("%y%m%d%H"), end_datetime.strftime("%y%m%d%H")))

    data = cursor.fetchall()

    conn.close()

    return data

def dms_to_float(dms_str):
    d, m = dms_str.split("°")
    m = m.strip("'")
    return float(d) + float(m) / 60

def haversine_distance(pos1, pos2):
    earth_radius = 6371  # 地球の半径 (km)
    lat1, lon1 = np.radians(pos1)
    lat2, lon2 = np.radians(pos2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return earth_radius * c

def interpolate_tide_data(data, target_latitude, target_longitude, power=2):


    positions = []
    tide_levels = []
    datetimes = []
    target_interpolated_tide_levels=[]
    for row in data:
        date, hour, latitude, longitude, tide_level = row
        positions.append((dms_to_float(latitude), dms_to_float(longitude)))
        tide_levels.append(tide_level)
        #３地点のデータからターゲットの潮位を図る
        if len(positions)% 3 == 0:
            datetimes.append(datetime.datetime.strptime(date, "%y%m%d") + datetime.timedelta(hours=hour))
            target_position = np.array([target_latitude, target_longitude])
            positions = np.array(positions)
            distances = [haversine_distance(target_position, pos) for pos in positions]
            weights = [1 / (dist**power) for dist in distances]
            target_interpolated_tide_level = sum(w * tide for w, tide in zip(weights, tide_levels)) / sum(weights)
            target_interpolated_tide_levels.append(target_interpolated_tide_level)
            positions = []
            tide_levels = []


    return datetimes, target_interpolated_tide_levels



import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

def plot_and_save_tide_graph(datetimes, tide_levels, get_date, get_hour, output_file):
    plt.plot(datetimes, tide_levels)
    print(datetimes)
    print(get_date)
    print(get_hour)
    # 魚が釣れた時間帯のマーカーを追加
    fish_caught_datetime = [dt for dt in datetimes if dt.date().day == get_date.day and dt.hour == get_hour]
    if fish_caught_datetime:
        fish_caught_tide_level = [tide_levels[datetimes.index(dt)] for dt in fish_caught_datetime]
        plt.scatter(fish_caught_datetime, fish_caught_tide_level, color="red", marker="o", label="Fish Caught Time")

    plt.xlabel("Time")
    plt.ylabel("Tide Level (cm)")

    date_formatter = DateFormatter("%m-%d %H:%M")
    plt.gca().xaxis.set_major_formatter(date_formatter)
    plt.gcf().autofmt_xdate()

    plt.legend()
    plt.savefig(output_file, format="jpeg")
    plt.clf()


def create_tide_graph(date, hour, target_latitude, target_longitude):
    data = get_tide_data(date, hour, target_latitude, target_longitude)
    print(data)
    if len(data) ==0 :
        return

    datetimes, tide_levels = interpolate_tide_data(data, target_latitude, target_longitude)
    print(datetimes)
    print(tide_levels)
    output_file = f"{str(session['temp_folder'])}/tide_graph_{date}_{hour}.jpeg"
    plot_and_save_tide_graph(datetimes, tide_levels,date, hour, output_file)
    return f"tide_graph_{date}_{hour}.jpeg"
