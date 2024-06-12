import requests
import json
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database URL
DATABASE_URL = 'postgresql://user:password@localhost/mydatabase'

# Create the database engine
engine = create_engine("sqlite:///mydb.db",echo=True)

# Define the Base
Base = declarative_base()

# Define the ProductTransaction model
class ProductTransaction(Base):
    __tablename__ = 'product_transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    description = Column(String)
    price = Column(Float)
    date_of_sale = Column(Date)
    category = Column(String)
    sold = Column(Boolean)

# Create the table
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Fetch data from the third-party API
response = requests.get('https://s3.amazonaws.com/roxiler.com/product_transaction.json')
data = response.json()

# Insert data into the database
for item in data:
    transaction = ProductTransaction(
        title=item['title'],
        description=item['description'],
        price=item['price'],
        date_of_sale=item['dateOfSale'],
        category=item['category'],
        sold=item['sold']
    )
    session.add(transaction)

session.commit()
session.close()
