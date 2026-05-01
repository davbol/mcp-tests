from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from uuid import UUID, uuid4
from enum import Enum

app = FastAPI(
    title="Bio Distributor Customer API",
    description="Mock API for managing customers of a bio vegetable distributor.",
    version="1.0.0",
)

class CustomerType(str, Enum):
    RESTAURANT = "Restaurant"
    RETAILER = "Retailer"
    PRIVATE = "Private"
    WHOLESALER = "Wholesaler"

class Address(BaseModel):
    street: str = Field(..., json_schema_extra={"example": "Main Street 123"})
    city: str = Field(..., json_schema_extra={"example": "Berlin"})
    zip_code: str = Field(..., json_schema_extra={"example": "10115"})
    country: str = Field(..., json_schema_extra={"example": "Germany"})

class CustomerBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Green Garden Restaurant"})
    email: EmailStr = Field(..., json_schema_extra={"example": "info@greengarden.de"})
    phone: str = Field(..., json_schema_extra={"example": "+49 30 12345678"})
    address: Address
    customer_type: CustomerType = Field(..., json_schema_extra={"example": CustomerType.RESTAURANT})
    is_active: bool = Field(default=True)
    loyalty_points: int = Field(default=0, ge=0)
    notes: Optional[str] = Field(None, json_schema_extra={"example": "Prefer morning deliveries."})

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: UUID = Field(default_factory=uuid4)

# In-memory database
customers_db: List[Customer] = [
    Customer(
        id=uuid4(),
        name="Bio Markt Sun",
        email="contact@biomarktsun.com",
        phone="+49 40 87654321",
        address=Address(street="Sonnenallee 45", city="Hamburg", zip_code="20095", country="Germany"),
        customer_type=CustomerType.RETAILER,
        loyalty_points=1250,
        notes="Key retailer in the northern region."
    ),
    Customer(
        id=uuid4(),
        name="Chef Pierre",
        email="pierre@bistro-bio.fr",
        phone="+33 1 23456789",
        address=Address(street="Rue de Rivoli 10", city="Paris", zip_code="75001", country="France"),
        customer_type=CustomerType.RESTAURANT,
        loyalty_points=500,
        notes="Exclusively uses Demeter certified products."
    )
]

@app.get("/customers", response_model=List[Customer], tags=["Customers"])
async def get_customers():
    """Retrieve all customers."""
    return customers_db

@app.get("/customers/{customer_id}", response_model=Customer, tags=["Customers"])
async def get_customer(customer_id: UUID):
    """Retrieve a specific customer by ID."""
    for customer in customers_db:
        if customer.id == customer_id:
            return customer
    raise HTTPException(status_code=404, detail="Customer not found")

@app.post("/customers", response_model=Customer, status_code=status.HTTP_201_CREATED, tags=["Customers"])
async def create_customer(customer_in: CustomerCreate):
    """Register a new customer."""
    new_customer = Customer(**customer_in.model_dump())
    customers_db.append(new_customer)
    return new_customer

@app.put("/customers/{customer_id}", response_model=Customer, tags=["Customers"])
async def update_customer(customer_id: UUID, customer_in: CustomerCreate):
    """Update customer information."""
    for index, customer in enumerate(customers_db):
        if customer.id == customer_id:
            updated_customer = Customer(id=customer_id, **customer_in.model_dump())
            customers_db[index] = updated_customer
            return updated_customer
    raise HTTPException(status_code=404, detail="Customer not found")

@app.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Customers"])
async def delete_customer(customer_id: UUID):
    """Remove a customer from the database."""
    for index, customer in enumerate(customers_db):
        if customer.id == customer_id:
            customers_db.pop(index)
            return
    raise HTTPException(status_code=404, detail="Customer not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
