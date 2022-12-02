from pymongo import MongoClient
from dotenv import load_dotenv
import os 
load_dotenv()
mongoDB = os.environ.get('mongoDB')
client = MongoClient(mongoDB)

db = client.test

doc = {'test':'test env'}

db.t.insert_one(doc)