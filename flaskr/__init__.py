from flask import Flask
app = Flask(__name__)
app.config["SECRET_KEY"] = "jaist-go-dev-secret-9f3a7c1b8e2d"
_flask_app = app
import flaskr.app
app = _flask_app
import flaskr.auth
