from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import pandas as pd
import logging
import os
import io

from db import SessionLocal, engine
from models import Base, Material
from blockchain import verify_source
from joblib import load

app = FastAPI(title="Eco Material Blockchain Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
Base.metadata.create_all(bind=engine)

# Load model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml_model.pkl")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class MaterialCreate(BaseModel):
    material: str
    quantity: int
    source: str
    carbon_savings: float
    project_location: str
    used_in_project: str
    date_added: str
    actual_usage: Optional[int] = None

class MaterialResponse(MaterialCreate):
    id: int

    class Config:
        orm_mode = True


@app.get("/", tags=["Health Check"])
def root():
    return {"message": "🌿 EcoBlock API is Live!"}


@app.get("/materials", response_model=List[MaterialResponse], tags=["Materials"])
def get_materials(db: Session = Depends(get_db)):
    return db.query(Material).limit(100).all()


@app.get("/materials/{material_id}", response_model=MaterialResponse, tags=["Materials"])
def get_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@app.post("/materials", response_model=MaterialResponse, tags=["Materials"])
def create_material(data: MaterialCreate, db: Session = Depends(get_db)):
    if not verify_source(data.source):
        raise HTTPException(status_code=400, detail="Source not verified")

    # Predict actual usage if not provided
    if data.actual_usage is None:
        try:
            model = load(MODEL_PATH)
            input_df = pd.DataFrame([{"carbon_savings": data.carbon_savings}])
            prediction = model.predict(input_df)[0]
            data.actual_usage = int(prediction)
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise HTTPException(status_code=500, detail="Prediction failed")

    new_material = Material(**data.dict())
    db.add(new_material)
    db.commit()
    db.refresh(new_material)
    return new_material


@app.get("/predict-by-id/{material_id}", tags=["Prediction"])
def predict_actual_usage(material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    try:
        model = load(MODEL_PATH)
        input_df = pd.DataFrame([{"carbon_savings": material.carbon_savings}])
        prediction = model.predict(input_df)[0]
        return {
            "material": material.material,
            "predicted_usage": int(prediction)
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")


@app.get("/analytics/carbon_savings", tags=["Analytics"])
def carbon_savings_summary(db: Session = Depends(get_db)):
    materials = db.query(Material).all()
    total = sum(m.carbon_savings for m in materials)
    avg = total / len(materials) if materials else 0
    return {"total": round(total, 2), "average": round(avg, 2)}


@app.get("/suggest-materials/{material_id}", tags=["Suggestions"])
def suggest_alternatives(material_id: int, db: Session = Depends(get_db)):
    current = db.query(Material).filter(Material.id == material_id).first()
    if not current:
        raise HTTPException(status_code=404, detail="Material not found")

    alternatives = (
        db.query(Material)
        .filter(Material.id != material_id)
        .filter(Material.carbon_savings > current.carbon_savings)
        .order_by(Material.carbon_savings.desc())
        .limit(5)
        .all()
    )

    return [
        {
            "id": m.id,
            "material": m.material,
            "carbon_savings": m.carbon_savings
        }
        for m in alternatives
    ]


@app.get("/materials/export", tags=["Export"])
def export_materials(db: Session = Depends(get_db)):
    materials = db.query(Material).yield_per(100)

    def generate():
        yield "id,material,quantity,source,carbon_savings,project_location,used_in_project,date_added,actual_usage\n"
        for m in materials:
            yield f'{m.id},"{m.material}",{m.quantity},"{m.source}",{m.carbon_savings},"{m.project_location}","{m.used_in_project}","{m.date_added}",{m.actual_usage}\n'

    return StreamingResponse(generate(), media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=materials_export.csv"
    })
