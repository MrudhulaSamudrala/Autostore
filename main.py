from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import orders, products, bins, bots
from db.database import Base, engine

print("About to create tables")
Base.metadata.create_all(bind=engine)
print("Tables created")

app = FastAPI()

# CORS middleware should be added before routers/static files
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files for product images
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(orders)
app.include_router(products)
app.include_router(bins)
app.include_router(bots)

@app.get("/")
def read_root():
    return {"Hello": "World"} 