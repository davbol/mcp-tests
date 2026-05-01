from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from enum import Enum

app = FastAPI(
    title="Bio Vegetable Distributor API",
    description="Mock API for managing products of a bio vegetable distributor. Includes full CRUD functionality and automatic OpenAPI documentation.",
    version="1.0.0",
)

class Category(str, Enum):
    ROOT = "Wurzelgemüse"
    LEAFY = "Blattgemüse"
    FRUIT = "Fruchtgemüse"
    BRASSICA = "Kohlgemüse"
    TUBER = "Knollengemüse"
    ALLIUM = "Zwiebelgemüse"
    LEGUME = "Hülsenfrüchte"

class Certification(str, Enum):
    EU_BIO = "EU-Bio"
    DEMETER = "Demeter"
    BIO_SUISSE = "Bio Suisse (Knospe)"
    NATURLAND = "Naturland"

class Unit(str, Enum):
    KG = "kg"
    PIECE = "piece"
    BUNCH = "bunch"
    BOX = "box"

class ProductBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Carrot"})
    category: Category = Field(..., json_schema_extra={"example": Category.ROOT})
    price_per_unit: float = Field(..., gt=0, json_schema_extra={"example": 2.50})
    unit: Unit = Field(..., json_schema_extra={"example": Unit.KG})
    origin: str = Field(..., json_schema_extra={"example": "Germany, Bavaria"})
    stock_quantity: float = Field(..., ge=0, json_schema_extra={"example": 150.0})
    certification: Certification = Field(..., json_schema_extra={"example": Certification.DEMETER})
    is_seasonal: bool = Field(default=True)
    description: Optional[str] = Field(None, json_schema_extra={"example": "Fresh, crunchy organic carrots from local farmers."})

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: UUID = Field(default_factory=uuid4)

# In-memory database
products_db: List[Product] = [
    Product(
        id=uuid4(),
        name="Bio Blattspinat",
        category=Category.LEAFY,
        price_per_unit=4.50,
        unit=Unit.BUNCH,
        origin="Schweiz, Seeland",
        stock_quantity=80,
        certification=Certification.BIO_SUISSE,
        is_seasonal=True,
        description="Frischer Bio Blattspinat aus regionalem Anbau."
    ),
    Product(
        id=uuid4(),
        name="Hokkaido Kürbis",
        category=Category.FRUIT,
        price_per_unit=3.80,
        unit=Unit.KG,
        origin="Schweiz, Thurgau",
        stock_quantity=150,
        certification=Certification.BIO_SUISSE,
        is_seasonal=True,
        description="Leuchtend oranger Speisekürbis mit essbarer Schale."
    ),
    Product(
        id=uuid4(),
        name="Kartoffeln (Charlotte)",
        category=Category.TUBER,
        price_per_unit=2.90,
        unit=Unit.KG,
        origin="Schweiz, Bern",
        stock_quantity=1200,
        certification=Certification.DEMETER,
        is_seasonal=False,
        description="Festkochende Bio-Speisekartoffeln."
    ),
    Product(
        id=uuid4(),
        name="Rüebli (Karotten)",
        category=Category.ROOT,
        price_per_unit=3.20,
        unit=Unit.KG,
        origin="Schweiz, Aargau",
        stock_quantity=500,
        certification=Certification.BIO_SUISSE,
        is_seasonal=False,
        description="Knackige Bio-Rüebli direkt vom Feld."
    ),
    Product(
        id=uuid4(),
        name="Lauch (Schnittlauch)",
        category=Category.ALLIUM,
        price_per_unit=2.50,
        unit=Unit.BUNCH,
        origin="Schweiz, Wallis",
        stock_quantity=200,
        certification=Certification.BIO_SUISSE,
        is_seasonal=True,
        description="Würziger Bio-Lauch für feine Gerichte."
    )
]

@app.get("/products", response_model=List[Product], tags=["Products"])
async def get_products():
    """Retrieve all products from the distributor."""
    return products_db

@app.get("/products/{product_id}", response_model=Product, tags=["Products"])
async def get_product(product_id: UUID):
    """Retrieve details of a specific product by its ID."""
    for product in products_db:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED, tags=["Products"])
async def create_product(product_in: ProductCreate):
    """Add a new product to the catalog."""
    new_product = Product(**product_in.model_dump())
    products_db.append(new_product)
    return new_product

@app.put("/products/{product_id}", response_model=Product, tags=["Products"])
async def update_product(product_id: UUID, product_in: ProductCreate):
    """Update an existing product's information."""
    for index, product in enumerate(products_db):
        if product.id == product_id:
            updated_product = Product(id=product_id, **product_in.model_dump())
            products_db[index] = updated_product
            return updated_product
    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Products"])
async def delete_product(product_id: UUID):
    """Remove a product from the catalog."""
    for index, product in enumerate(products_db):
        if product.id == product_id:
            products_db.pop(index)
            return
    raise HTTPException(status_code=404, detail="Product not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
