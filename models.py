from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(255))
    description = db.Column(db.String(1000))
    image_url = db.Column(db.String(500))
    sustainability_info = db.Column(db.String(500))
    price = db.Column(db.String(50))
    category = db.Column(db.String(100))

def __repr__(self):
        return f"<Product {self.name}>"

