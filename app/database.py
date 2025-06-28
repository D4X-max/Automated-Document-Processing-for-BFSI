import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Connection String to our local Docker MongoDB instance
MONGO_URI = "mongodb://root:example@localhost:27017/"

try:
    # Set a timeout to prevent the app from hanging indefinitely
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # The ismaster command is a lightweight way to test the connection.
    client.admin.command('ismaster')
    print("✅ MongoDB connection successful.")

except ConnectionFailure as e:
    print(f"❌ MongoDB connection failed. Error: {e}")
    print("---")
    print("Please ensure your MongoDB Docker container is running.")
    print("You can start it with: docker-compose up -d")
    # Exit the application if the database connection fails on startup.
    sys.exit("Database connection is required to run the application.")

# If the connection is successful, we can safely define our collections.
db = client.bfsi_doc_processing
pan_collection = db.pan_cards
aadhaar_collection = db.aadhaar_cards

