import os
from dotenv import load_dotenv
import functools
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3

from flaskr import app, auth
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

# .envを読み込む
load_dotenv()

app = Flask(__name__)

DB_NAME = os.getenv("DB_NAME", "map.db")

# Flaskの設定に環境変数をセット
app.config["google_map_api_key"] = os.getenv("google_map_api_key")

REVIEW_DATA_PATH = Path(__file__).resolve().parent / "data" / "reviews.json"
POST_DATA_PATH = Path(__file__).resolve().parent / "data" / "posts.json"
USERS_DATA_PATH = Path(__file__).resolve().parent / "data" / "users.json"

CATEGORY_TAGS = {
    "ride": ["車募集"],
    "event": ["遊び"],
    "soon": ["急ぎ"],
}


def load_reviews():
    if not REVIEW_DATA_PATH.exists():
        return []

    with REVIEW_DATA_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def save_reviews(reviews):
    REVIEW_DATA_PATH.parent.mkdir(exist_ok=True)
    with REVIEW_DATA_PATH.open("w", encoding="utf-8") as file:
        json.dump(reviews, file, ensure_ascii=False, indent=2)


def format_review(review):
    created_at = datetime.fromisoformat(review["created_at"])
    return {
        **review,
        "created_label": created_at.astimezone(timezone(timedelta(hours=9))).strftime("%Y/%m/%d %H:%M"),
    }


def load_posts():
    if not POST_DATA_PATH.exists():
        return []
    with POST_DATA_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def save_posts(posts):
    POST_DATA_PATH.parent.mkdir(exist_ok=True)
    with POST_DATA_PATH.open("w", encoding="utf-8") as file:
        json.dump(posts, file, ensure_ascii=False, indent=2)


def get_username(user_id):
    if not USERS_DATA_PATH.exists():
        return "Unknown"
    with USERS_DATA_PATH.open(encoding="utf-8") as file:
        users = json.load(file)
    user = next((u for u in users if u["id"] == user_id), None)
    return user["username"] if user else "Unknown"


def api_login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "ログインが必要です"}), 401
        return f(*args, **kwargs)
    return decorated


def build_review_ranking(reviews):
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_shop_names = [
        review["shop_name"]
        for review in reviews
        if datetime.fromisoformat(review["created_at"]) >= one_month_ago
    ]
    return Counter(recent_shop_names).most_common(5)

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

@app.route("/demo/board")
def demo_board():
    return render_template("demo_board.html")


@app.route("/demo/posts/<int:post_id>")
def demo_post(post_id):
    return render_template("demo_post.html", post_id=post_id)

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

# @app.route('/')
# def index():
#     return render_template(
#         'index.html'
#         )
    
@app.route("/", methods=["GET", "POST"])
@auth.login_required
def demo_board():
    reviews = load_reviews()
    review_error = None

    if request.method == "POST":
        shop_name = request.form.get("shop_name", "").strip()
        comment = request.form.get("comment", "").strip()
        rating_text = request.form.get("rating", "")

        try:
            rating = int(rating_text)
        except ValueError:
            rating = 0

        if not shop_name or not comment or rating not in range(1, 6):
            review_error = "店名、星評価、口コミ本文をすべて入力してください。"
        else:
            next_id = max((review["id"] for review in reviews), default=0) + 1
            reviews.append(
                {
                    "id": next_id,
                    "shop_name": shop_name,
                    "rating": rating,
                    "comment": comment,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            save_reviews(reviews)
            return redirect(url_for("demo_board", review="posted") + "#reviews")

    sorted_reviews = sorted(reviews, key=lambda review: review["created_at"], reverse=True)
    return render_template(
        "demo_board.html",
        reviews=[format_review(review) for review in sorted_reviews],
        review_ranking=build_review_ranking(reviews),
        review_error=review_error,
        review_posted=request.args.get("review") == "posted",
    )


@app.route("/posts/<int:post_id>")
@auth.login_required
def demo_post(post_id):
    return render_template("demo_post.html", post_id=post_id)

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
@app.route("/api/posts", methods=["GET"])
@api_login_required
def api_get_posts():
    posts = load_posts()
    category = request.args.get("category", "all")
    query = request.args.get("q", "").strip().lower()

    if category != "all":
        posts = [p for p in posts if p["category"] == category]

    if query:
        posts = [
            p for p in posts
            if query in " ".join([
                p.get("title", ""), p.get("destination", ""), p.get("meeting", ""),
                p.get("contact", ""), p.get("summary", ""), *p.get("tags", [])
            ]).lower()
        ]

    posts = sorted(posts, key=lambda p: p["created_at"], reverse=True)
    return jsonify(posts)


@app.route("/api/posts", methods=["POST"])
@api_login_required
def api_create_post():
    data = request.get_json()
    if not data:
        return jsonify({"error": "リクエストが不正です"}), 400

    title = data.get("title", "").strip()
    category = data.get("category", "")
    destination = data.get("destination", "").strip()
    time = data.get("time", "").strip()
    meeting = data.get("meeting", "").strip()
    people = data.get("people", "").strip()
    contact = data.get("contact", "").strip()
    cost = data.get("cost", "").strip()
    detail = data.get("detail", "").strip()

    if not all([title, category, destination, time, meeting, people, contact, detail]):
        return jsonify({"error": "必須項目をすべて入力してください"}), 400

    if category not in CATEGORY_TAGS:
        return jsonify({"error": "カテゴリが不正です"}), 400

    user_id = session["user_id"]
    owner = get_username(user_id)
    summary = detail[:50] + ("…" if len(detail) > 50 else "")

    posts = load_posts()
    next_id = max((p["id"] for p in posts), default=0) + 1
    new_post = {
        "id": next_id,
        "title": title,
        "category": category,
        "tags": CATEGORY_TAGS[category],
        "status": "募集中",
        "destination": destination,
        "time": time,
        "meeting": meeting,
        "people": people,
        "contact": contact,
        "cost": cost,
        "summary": summary,
        "detail": detail,
        "user_id": user_id,
        "owner": owner,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    posts.append(new_post)
    save_posts(posts)
    return jsonify(new_post), 201


@app.route("/api/posts/<int:post_id>", methods=["GET"])
@api_login_required
def api_get_post(post_id):
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": "募集が見つかりません"}), 404
    return jsonify({**post, "is_owner": post["user_id"] == session["user_id"]})


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
@api_login_required
def api_delete_post(post_id):
    posts = load_posts()
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": "募集が見つかりません"}), 404
    if post["user_id"] != session["user_id"]:
        return jsonify({"error": "削除権限がありません"}), 403
    save_posts([p for p in posts if p["id"] != post_id])
    return jsonify({"message": "削除しました"})
