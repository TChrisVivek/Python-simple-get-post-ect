from fastapi import FastAPI
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# MongoDB connection using your new fastapi_user credentials
MONGO_URL = "mongodb+srv://fastapi_user:python123456@cluster0.gyjrmuf.mongodb.net/?authSource=admin"

client = AsyncIOMotorClient(
    MONGO_URL, 
    tls=True, 
    tlsAllowInvalidCertificates=True
)

db = client.ai_project_db
item_collection = db.get_collection("items")

class Item(BaseModel):
    name: str
    content: str

@app.post("/items")
async def create_item(new_item: Item):
    try:
        item_dict = new_item.model_dump()
        result = await item_collection.insert_one(item_dict)
        return {
            "message": "Item added Successfully",
            "id": str(result.inserted_id)
        }
    except Exception as e:
        print(f"🚨 MONGODB ERROR: {e}")
        return {"error": str(e)}

@app.get("/items")
async def get_all_items():
    items = []
    cursor = item_collection.find({})
    async for document in cursor:
        document["_id"] = str(document["_id"])
        items.append(document)
    return {"Items": items}