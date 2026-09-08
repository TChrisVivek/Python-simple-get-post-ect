import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


load_dotenv()

app = FastAPI()


DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_CLUSTER = os.getenv("DB_CLUSTER")


MONGO_URL = f"mongodb+srv://{DB_USER}:{DB_PASS}@{DB_CLUSTER}/?authSource=admin"
print(f"🔌 Attempting MongoDB connection with username: '{DB_USER}'")

client = AsyncIOMotorClient(MONGO_URL, tls=True, tlsAllowInvalidCertificates=True)
items_db = client.ai_project_db.items

class Item(BaseModel):
    name: str
    content: str

@app.post("/items")
async def create(item: Item):
    res = await items_db.insert_one(item.model_dump())
    return {"message": "Success", "id": str(res.inserted_id)}

@app.get("/items")
async def get_all():
    items = await items_db.find().to_list(100)
    for i in items: i["_id"] = str(i["_id"])
    return {"Items": items}


@app.put("/item/{item_id}")
async def update_item(item_id: str, item:Item):
    result = await items_db.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": item.model_dump()}
    )
    return {"message": "Item Updated", "modified_count": result.modified_count}


@app.delete("/item/{item_id}")
async def delete_item(item_id: str):
    result = await items_db.delete_one({"_id": ObjectId(item_id)})
    return {"message": "Item Deleted", "deleted_count": result.deleted_count}