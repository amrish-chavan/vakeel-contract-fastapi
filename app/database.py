from config import MONGODB_URI
from pymongo import MongoClient

client = MongoClient(MONGODB_URI)
db = client["mydb"]

# collections
contract_collection = db.get_collection("contracts")
analysis_collection = db.get_collection("analysis")

def init_db():
    contract_collection.create_index("filename", unique=True)
    analysis_collection.create_index("contract_id", unique=True)
