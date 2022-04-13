from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://am5391:g7hwpp5h@pgserver.mau.se/Onlineshopz'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

db = SQLAlchemy(app)