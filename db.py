from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGO_URI"))

ads_manager_db = mongo_client["ads_manager_db"]

users_collection = ads_manager_db["Users"]

companies_collection = ads_manager_db["Companies"]

jobs_collection = ads_manager_db["Jobs"]

applications_collection = ads_manager_db["Applications"]

categories_collection = ads_manager_db["Categories"]