from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGO_URI"))

ads_manager_db = mongo_client["ads_manager_db"]