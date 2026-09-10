import os
from dotenv import load_dotenv
from fastapi import FastAPI,Query, HTTPException
from pydantic import BaseModel, Field
from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse



load_dotenv()

app = FastAPI()


DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_CLUSTER = os.getenv("DB_CLUSTER")


MONGO_URL = f"mongodb+srv://{DB_USER}:{DB_PASS}@{DB_CLUSTER}/?authSource=admin"
print(f" Attempting MongoDB connection with username: '{DB_USER}'")

client = AsyncIOMotorClient(MONGO_URL, tls=True, tlsAllowInvalidCertificates=True)
items_db = client.ai_project_db.items

@app.exception_handler(RequestValidationError)
async def custom_validation_error(request, exc):
    # exc.errors() contains the original bulky list of errors
    error = exc.errors()[0]
    
    # Extract the name of the field that failed (e.g., 'content', 'name', 'password')
    field_name = error["loc"][-1]
    
    # Check if the error is specifically because the string is too short
    if error["type"] == "string_too_short":
        min_len = error["ctx"]["min_length"]
        custom_message = f"{field_name.capitalize()} should have at least {min_len} character(s)"
    else:
        # A fallback message for other rules (like invalid data types)
        custom_message = f"Invalid input for {field_name}"

    # Return the ultra-clean JSON format
    return JSONResponse(
        status_code=422,
        content={"error": custom_message}
    )

class Item(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    content: str = Field(min_length=1)

@app.post("/items")
async def create(item: Item):
    res = await items_db.insert_one(item.model_dump())
    return {"message": "Success", "id": str(res.inserted_id)}

# @app.get("/items")
# async def get_all():
#     items = await items_db.find().to_list(100)
#     for i in items: i["_id"] = str(i["_id"])
#     return {"Items": items}


@app.get("/items")
async def get_all(limit: int = 100):
    items =await items_db.find().to_list(limit)
    for i in items: i["_id"] = str(i["_id"])
    return {"items": items}





@app.get("/items/{item_id}")
async def get_single_item(item_id: str):
    try:
        item = await items_db.find_one({"_id": ObjectId(item_id)})
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        item["_id"] = str(item["_id"])
        return item

    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid MongoDb ID format")

@app.put("/item/{item_id}")
async def update_item(item_id: str, item:Item):
    try:
        result = await items_db.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": item.model_dump()}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Item not found")

        return {"message": "Item updated", "modified_count": result.modified_count}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid MondgoDB ID format")


@app.delete("/item/{item_id}")
async def delete_item(item_id: str):
    try: 
        result = await items_db.delete_one({"_id": ObjectId(item_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message": "Item Deleted", "deleted_count": result.deleted_count}

    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid MongoDB ID format")
