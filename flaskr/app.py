from flask import Flask, render_template
import sqlite3
import os
from dotenv import load_dotenv

# .envを読み込む
load_dotenv()

app = Flask(__name__)

DB_NAME = os.getenv("DB_NAME", "map.db")

# Flaskの設定に環境変数をセット
app.config["google_map_api_key"] = os.getenv("google_map_api_key")

def get_map_data_by_id(data_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        row = conn.execute("""
            SELECT
                id,
                latitude,
                longitude,
                place_name
            FROM map_information
            WHERE id = ?
        """, (data_id,)).fetchone()

    return dict(row) if row else None

@app.route("/")
def index():
    location = {
        "lat": 35.6811673,
        "lng": 139.7670516,
        "title": "東京駅"
    }

    return render_template(
        "index.html",
        location=location,
        google_map_api_key=app.config["google_map_api_key"]
    )

@app.route("/map/<int:data_id>")
def show_map(data_id):
    location = get_map_data_by_id(data_id)

    if location is None:
        return "データが見つかりません", 404

    return render_template(
        "index.html",
        location={
            "lat": location["latitude"],
            "lng": location["longitude"],
            "title": location["place_name"]
        },
        google_map_api_key=app.config["google_map_api_key"]
    )

@app.cli.command("create-db")
def create_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS map_information (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                place_name TEXT NOT NULL
            )
        """)
    print("テーブルを作成しました")


@app.cli.command("insert-sample")
def insert_sample():
    with sqlite3.connect(DB_NAME) as conn:
        conn.executemany("""
            INSERT INTO map_information
            (latitude, longitude, place_name)
            VALUES (?, ?, ?)
        """, [
            (35.681236, 139.767125, "東京駅"),
            (35.658584, 139.745431, "東京タワー"),
            (34.693725, 135.502254, "大阪駅")
        ])
    print("サンプルデータを登録しました")


@app.cli.command("add-data")
def add_data():
    latitude = float(input("緯度: "))
    longitude = float(input("経度: "))
    place_name = input("場所名: ")

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT INTO map_information
            (latitude, longitude, place_name)
            VALUES (?, ?, ?)
        """, (latitude, longitude, place_name))

    print("データを追加しました")


@app.cli.command("show-data")
def show_data():
    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute("""
            SELECT latitude, longitude, place_name
            FROM map_information
        """).fetchall()

    for lat, lng, name in rows:
        print(f"{name}: ({lat}, {lng})")


if __name__ == "__main__":
    app.run(debug=True)