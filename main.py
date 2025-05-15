from fastapi import FastAPI, HTTPException, Path, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Simple API",
    description="A simple REST API built with FastAPI",
    version="0.1.0"
)

# Sample data - in a real app, you'd use a database
items_db = {
    1: {"id": 1, "name": "Item 1", "description": "This is item 1", "price": 50.2},
    2: {"id": 2, "name": "Item 2", "description": "This is item 2", "price": 30.5},
    3: {"id": 3, "name": "Item 3", "description": "This is item 3", "price": 45.0},
}

# Pydantic models for request/response validation
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    price: float

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Simple API"}

# Get all items
@app.get("/items/", response_model=List[Item])
async def get_items(skip: int = Query(0, description="Skip these many items"), 
                    limit: int = Query(10, description="Limit the number of items returned")):
    items = list(items_db.values())
    return items[skip:skip + limit]

# Get a specific item by ID
@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int = Path(..., description="The ID of the item to get")):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

# Create a new item
@app.post("/items/", response_model=Item, status_code=201)
async def create_item(item: Item):
    # Generate a new ID if not provided
    if item.id is None:
        item.id = max(items_db.keys()) + 1 if items_db else 1
    
    # Check if ID already exists
    if item.id in items_db:
        raise HTTPException(status_code=400, detail="Item ID already exists")
    
    items_db[item.id] = item.dict()
    return item

# Update an existing item
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item_update: ItemUpdate):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Update only provided fields
    current_item = items_db[item_id]
    update_data = item_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        if value is not None:
            current_item[key] = value
    
    return current_item

# Delete an item
@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    del items_db[item_id]
    return None

# Run the API with uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
