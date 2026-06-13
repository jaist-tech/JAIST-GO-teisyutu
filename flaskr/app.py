import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flaskr import app
from flask import redirect, render_template, request, url_for


REVIEW_DATA_PATH = Path(__file__).resolve().parent / "data" / "reviews.json"


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


def build_review_ranking(reviews):
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_shop_names = [
        review["shop_name"]
        for review in reviews
        if datetime.fromisoformat(review["created_at"]) >= one_month_ago
    ]
    return Counter(recent_shop_names).most_common(5)

@app.route('/')
def index():
    return render_template(
        'index.html'
        )
    
@app.route("/demo/board", methods=["GET", "POST"])
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


@app.route("/demo/posts/<int:post_id>")
def demo_post(post_id):
    return render_template("demo_post.html", post_id=post_id)
