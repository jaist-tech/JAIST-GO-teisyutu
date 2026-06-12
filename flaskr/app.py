from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    location = {
        "lat": 35.6811673,
        "lng": 139.7670516,
        "title": "東京駅"
    }

    return render_template("index.html", location=location, google_map_api_key=app.config["google_map_api_key"])

if __name__ == "__main__":
    app.run(debug=True)