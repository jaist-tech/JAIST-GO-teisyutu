from flaskr import app
from flask import render_template

@app.route('/')
def index():
    return render_template(
        'index.html'
        )
    
@app.route("/demo/board")
def demo_board():
    return render_template("demo_board.html")


@app.route("/demo/posts/<int:post_id>")
def demo_post(post_id):
    return render_template("demo_post.html", post_id=post_id)