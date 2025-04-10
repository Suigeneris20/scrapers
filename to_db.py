from urllib.parse import quote_plus #to solve special character in password
from flask import Flask
from models import db, Product
import json

app = Flask(__name__)
password = "****************"
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://ife:{quote_plus(password)}@localhost:5432/fashion_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Load scraped data (assume it's a JSON file)
with open('scraped_data.json', 'r') as f:
    scraped_items = json.load(f)

# Insert into database
with app.app_context():
    for item in scraped_items:
        gallery=item['item gallery']
        sustain_info=item['item sustainablibilty info']
        sustain_info = ', '.join(sustain_info)

        if isinstance(gallery, list):
            
            for url in gallery:
                product = Product(
                    name=item['item name'],
                    description=item['item description'],
                    image_url=url,
                    sustainability_info=sustain_info,
                    #price=item['price'],
                    #category=item['category']
                )
                db.session.add(product)
        
        else:
            product = Product(
                name=item['item name'],
                description=item['item description'],
                image_url=gallery,
                sustainability_info=sustain_info,
                #price=item['price'],
                #category=item['category']
            )
            db.session.add(product)
    db.session.commit()

print("Scraped data inserted successfully!")

