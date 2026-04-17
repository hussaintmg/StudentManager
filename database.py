import os
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client["student_manager_db"]
students_collection = db["students"]

async def check_connection():
    try:
        await client.admin.command('ping')
        print("Successfully connected to MongoDB.")
    except Exception as e:
        print(f"MongoDB Connection Error: {e}")
