import cloudinary
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = "!@#$%^&*()"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/phongmachdb?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)
login = LoginManager(app)

cloudinary.config(cloud_name='dstjar2iy',
                  api_key='929341466922158',
                  api_secret='ZydOWhhvZkUfCfoOIwuTYObfmbM')