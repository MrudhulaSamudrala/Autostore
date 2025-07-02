from fastapi import FastAPI
from routers import orders, products, bins, bots
from db.database import Base, engine

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(orders)
app.include_router(products)
app.include_router(bins)
app.include_router(bots) 