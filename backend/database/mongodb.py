from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))

db = client["customer_support_ai"]

chat_collection = db["chat_history"]

users_collection = db["users"]

ticket_collection = db["tickets"]
