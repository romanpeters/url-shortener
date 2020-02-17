from flask import Flask

app = Flask(__name__)
app.config.from_object('flask_config')

from app import views, api
