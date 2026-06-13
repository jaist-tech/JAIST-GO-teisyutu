from flask import Flask
app = Flask(__name__)
_flask_app = app
import flaskr.app
app = _flask_app
