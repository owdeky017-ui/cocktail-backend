from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db


Base.metadata.create_all(bind=engine)


app = FastAPI(title="Cocktail App", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/cocktails", response_model=list[schemas.Cocktail])
def list_cocktails(
    q: str | None = Query(default=None, min_length=1, max_length=50),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(models.Cocktail)

    if q:
        query = query.filter(models.Cocktail.name.ilike(f"%{q}%"))

    cocktails = query.offset(skip).limit(limit).all()
    return cocktails


@app.get("/cocktails/{cocktail_id}", response_model=schemas.Cocktail)
def get_cocktail(cocktail_id: int, db: Session = Depends(get_db)):
    cocktail = db.query(models.Cocktail).filter(models.Cocktail.id == cocktail_id).first()
    if not cocktail:
        raise HTTPException(status_code=404, detail="Cocktail not found")
    return cocktail


@app.post("/cocktails", response_model=schemas.Cocktail, status_code=201)
def create_cocktail(payload: schemas.CocktailCreate, db: Session = Depends(get_db)):
    exists = db.query(models.Cocktail).filter(models.Cocktail.name == payload.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Cocktail with this name already exists")
    cocktail = models.Cocktail(**payload.model_dump())
    db.add(cocktail)
    db.commit()
    db.refresh(cocktail)
    return cocktail
