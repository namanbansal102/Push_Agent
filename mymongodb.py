from pymongo import MongoClient, errors
from dotenv import load_dotenv
import os
from web3 import Web3

# Load environment variables
load_dotenv(

)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/" \
"")
DB_NAME = "PushChainAgent"
COLLECTION_NAME = "address_book"

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Create indexes for better performance
collection.create_index("username", unique=True)
collection.create_index("address", unique=False)

def add_to_book(username: str, address: str) -> str:
    """Add a user and their Push Chain address to the address book"""
    try:
        # Validate Ethereum address format
        if not Web3.is_address(address):
            return f"Invalid address format: {address}"
        
        # Convert to checksum address
        checksum_address = Web3.to_checksum_address(address)
        
        # Insert or update user
        result = collection.update_one(
            {"username": username},
            {"$set": {"address": checksum_address}},
            upsert=True
        )
        
        if result.upserted_id:
            return f"✅ Added {username} with address {checksum_address}"
        else:
            return f"✅ Updated {username} with new address {checksum_address}"
            
    except errors.DuplicateKeyError:
        return f"❌ Username {username} already exists. Use update_address to modify."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def fetch_address_from_book(username: str) -> str:
    """Retrieve address for a given username"""
    try:
        user = collection.find_one({"username": username})
        if user:
            return user['address']
        return f"❌ No address found for {username}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def update_address(username: str, new_address: str) -> str:
    """Update address for existing user"""
    try:
        if not Web3.is_address(new_address):
            return f"❌ Invalid address format: {new_address}"
        
        checksum_address = Web3.to_checksum_address(new_address)
        
        result = collection.update_one(
            {"username": username},
            {"$set": {"address": checksum_address}}
        )
        
        if result.modified_count > 0:
            return f"✅ Updated address for {username} to {checksum_address}"
        return f"❌ User {username} not found"
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

def delete_user(username: str) -> str:
    """Remove user from address book"""
    try:
        result = collection.delete_one({"username": username})
        if result.deleted_count > 0:
            return f"✅ Removed {username} from address book"
        return f"❌ User {username} not found"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def list_all_users() -> str:
    """List all users in the address book"""
    try:
        users = list(collection.find({}, {"_id": 0, "username": 1, "address": 1}))
        if users:
            result = "📞 Address Book:\n"
            for user in users:
                result += f"  • {user['username']}: {user['address']}\n"
            return result
        return "📭 Address book is empty"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def search_users(query: str) -> str:
    """Search users by username or address"""
    try:
        regex_query = {"$regex": query, "$options": "i"}
        users = list(collection.find({
            "$or": [
                {"username": regex_query},
                {"address": regex_query}
            ]
        }, {"_id": 0, "username": 1, "address": 1}))
        
        if users:
            result = f"🔍 Search results for '{query}':\n"
            for user in users:
                result += f"  • {user['username']}: {user['address']}\n"
            return result
        return f"❌ No users found matching '{query}'"
    except Exception as e:
        return f"❌ Error: {str(e)}"