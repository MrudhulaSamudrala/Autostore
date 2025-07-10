from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.products import Product
from models.bins import Bin
from typing import List
from schemas.products import ProductOut  # import the schema
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/products", tags=["products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RefillRequest(BaseModel):
    bin_id: int
    product_id: int
    quantity: int = 1

@router.get("/", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@router.post("/refill")
def refill_bin(refill_data: RefillRequest, db: Session = Depends(get_db)):
    """Refill a bin by updating last refill date for existing products"""
    try:
        # Check if bin exists
        bin_obj = db.query(Bin).filter(Bin.id == refill_data.bin_id).first()
        if not bin_obj:
            raise HTTPException(status_code=404, detail=f"Bin {refill_data.bin_id} not found")
        
        # Get all products assigned to this bin
        bin_products = db.query(Product).filter(Product.bin_id == refill_data.bin_id).all()
        
        if not bin_products:
            raise HTTPException(status_code=404, detail=f"No products assigned to Bin {refill_data.bin_id}")
        
        # Update last refill date for all products in this bin
        current_time = datetime.now()
        for product in bin_products:
            product.last_refilled = current_time
        
        # Update bin status to available
        bin_obj.status = "available"
        
        db.commit()
        db.refresh(bin_obj)
        
        # Get product names for response
        product_names = [p.name for p in bin_products]
        
        return {
            "message": f"Successfully refilled Bin {refill_data.bin_id} with existing products",
            "bin_id": refill_data.bin_id,
            "products": product_names,
            "last_refilled": current_time.isoformat(),
            "bin_status": bin_obj.status,
            "product_count": len(bin_products)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to refill bin: {str(e)}")

@router.post("/refill-multiple")
def refill_multiple_bins(refill_data: List[RefillRequest], db: Session = Depends(get_db)):
    """Refill multiple bins at once"""
    results = []
    
    for refill_item in refill_data:
        try:
            # Check if bin exists
            bin_obj = db.query(Bin).filter(Bin.id == refill_item.bin_id).first()
            if not bin_obj:
                results.append({
                    "bin_id": refill_item.bin_id,
                    "status": "failed",
                    "message": f"Bin {refill_item.bin_id} not found"
                })
                continue
            # Get the product in this bin matching the refill_item.product_id
            product = db.query(Product).filter(Product.bin_id == refill_item.bin_id, Product.id == refill_item.product_id).first()
            if not product:
                results.append({
                    "bin_id": refill_item.bin_id,
                    "product_id": refill_item.product_id,
                    "status": "failed",
                    "message": f"Product {refill_item.product_id} not found in Bin {refill_item.bin_id}"
                })
                continue
            # Update last refill date and increment quantity
            current_time = datetime.now()
            product.last_refilled = current_time
            if hasattr(product, 'quantity'):
                product.quantity = (product.quantity or 0) + refill_item.quantity
            # Update bin status to available
            bin_obj.status = "available"
            results.append({
                "bin_id": refill_item.bin_id,
                "product_id": refill_item.product_id,
                "product_name": product.name,
                "status": "success",
                "message": f"Successfully refilled Bin {refill_item.bin_id} with {product.name}",
                "last_refilled": current_time.isoformat(),
                "quantity": product.quantity
            })
        except Exception as e:
            results.append({
                "bin_id": refill_item.bin_id,
                "product_id": getattr(refill_item, 'product_id', None),
                "status": "failed",
                "message": f"Error: {str(e)}"
            })
    
    db.commit()
    return {"results": results} 