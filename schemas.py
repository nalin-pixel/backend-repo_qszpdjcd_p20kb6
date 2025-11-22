"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Chat app schemas

class ChatUser(BaseModel):
    """
    Users participating in chat rooms
    Collection name: "chatuser"
    """
    username: str = Field(..., description="Unique display name")
    # You can extend with auth fields later (password hash, etc.)
    is_active: bool = Field(default=True)

class Message(BaseModel):
    """
    Chat messages
    Collection name: "message"
    """
    room: str = Field(..., description="Room identifier")
    sender: str = Field(..., description="Sender username")
    content: str = Field(..., description="Message text")
    timestamp: Optional[datetime] = Field(default=None, description="UTC timestamp; set server-side")

# Example schemas (kept for reference)
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
