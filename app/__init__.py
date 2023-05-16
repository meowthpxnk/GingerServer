from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from redis import Redis
from custom_redis import CustomRedis

from .cfg import Config

app = Flask(__name__)

CORS(app)
cors = CORS(app, resources = {
    r"*":{
        "origins": "*"
    }
})

app.config.from_object(Config)
socket = SocketIO(app, cors_allowed_origins="*")

app_ctx = app.app_context()
app_ctx.push()

db = SQLAlchemy(app)

default_redis = Redis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)
redis_db = CustomRedis(default_redis)

Migrate(app, db, render_as_batch=True)

from app import views, models