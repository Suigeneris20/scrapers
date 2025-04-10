from urllib.parse import quote_plus #to solve special character in password
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Product
import os

app = Flask(__name__)

# Configure Database
password = "*********"
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://ife:{quote_plus(password)}@localhost:5432/fashion_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)

if __name__ == "__main__":
    app.run(debug=True)

