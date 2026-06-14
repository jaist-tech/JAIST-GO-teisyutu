import json
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

from flaskr import app
from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash


USER_DATA_PATH = Path(__file__).resolve().parent / "data" / "users.json"


# ---------------------------------------------------------------------------
# データの読み書き（口コミの reviews.json と同じ作法）
# ---------------------------------------------------------------------------
def load_users():
    if not USER_DATA_PATH.exists():
        return []

    with USER_DATA_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def save_users(users):
    USER_DATA_PATH.parent.mkdir(exist_ok=True)
    with USER_DATA_PATH.open("w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=2)


def find_user(username):
    """ユーザー名でユーザーを1件探す（大文字小文字は区別しない）。"""
    target = username.strip().lower()
    for user in load_users():
        if user["username"].lower() == target:
            return user
    return None


# ---------------------------------------------------------------------------
# ログイン必須にしたいルートに付けるデコレーター
#   使い方:  @login_required の行を @app.route(...) の下に足すだけ
# ---------------------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def current_user():
    """ログイン中ならユーザー情報、未ログインなら None を返す。"""
    user_id = session.get("user_id")
    if user_id is None:
        return None
    for user in load_users():
        if user["id"] == user_id:
            return user
    return None


# テンプレート側で {{ current_user }} を使えるようにする
@app.context_processor
def inject_current_user():
    return {"current_user": current_user()}


# ---------------------------------------------------------------------------
# ルート
# ---------------------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        if not username or not password:
            error = "ユーザー名とパスワードを入力してください。"
        elif len(username) > 50:
            error = "ユーザー名は50文字以内にしてください。"
        elif len(password) < 8:
            error = "パスワードは8文字以上にしてください。"
        elif password != password_confirm:
            error = "確認用パスワードが一致しません。"
        elif find_user(username) is not None:
            error = "そのユーザー名はすでに使われています。"
        else:
            users = load_users()
            next_id = max((user["id"] for user in users), default=0) + 1
            users.append(
                {
                    "id": next_id,
                    "username": username,
                    "password_hash": generate_password_hash(password),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            save_users(users)
            flash("登録が完了しました。ログインしてください。")
            return redirect(url_for("login"))

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = find_user(username)

        # ユーザーが居ない場合もハッシュ照合と同じ流れにすると親切だが、
        # ここではシンプルにまとめて「どちらが違うか」は伝えない作りにする。
        if user is None or not check_password_hash(user["password_hash"], password):
            error = "ユーザー名またはパスワードが違います。"
        else:
            session.clear()
            session["user_id"] = user["id"]
            # オープンリダイレクト対策: 同一サイト内のパスだけ許可する
            next_url = request.args.get("next", "")
            if next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)
            return redirect(url_for("demo_board"))

    return render_template("login.html", error=error)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("ログアウトしました。")
    return redirect(url_for("demo_board"))
