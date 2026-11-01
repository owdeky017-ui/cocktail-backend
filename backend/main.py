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
    ingredient_ids = [item.ingredient_id for item in payload.items]
    if ingredient_ids:
        existing_ingredients = db.query(models.Ingredient.id).filter(models.Ingredient.id.in_(ingredient_ids)).all()
        existing_ids = {id for (id,) in existing_ingredients}
        missing_ids = set(ingredient_ids) - existing_ids
        if missing_ids:
            raise HTTPException(status_code=400, detail=f"Ingredients with IDs {missing_ids} do not exist")
    cocktail = models.Cocktail(**payload.model_dump(exclude={"items"}))
    for item in payload.items:
        recipe_item = models.RecipeItem(
            quantity=item.quantity,
            unit=item.unit,
            ingredient_id=item.ingredient_id
        )
        cocktail.items.append(recipe_item)
    db.add(cocktail)
    db.commit()
    db.refresh(cocktail)
    return cocktail


@app.put("/cocktails/{cocktail_id}", response_model=schemas.Cocktail)
def update_cocktail(cocktail_id: int, payload: schemas.CocktailCreate, db: Session = Depends(get_db)):
    cocktail = db.query(models.Cocktail).filter(models.Cocktail.id == cocktail_id).first()
    if not cocktail:
        raise HTTPException(status_code=404, detail="Cocktail not found")
    clash = db.query(models.Cocktail).filter(models.Cocktail.name == payload.name, models.Cocktail.id != cocktail_id).first()
    if clash:
        raise HTTPException(status_code=400, detail="Cocktail with this name already exists")
    cocktail.name = payload.name
    cocktail.instructions = payload.instructions
    cocktail.glass = payload.glass
    cocktail.category = payload.category
    cocktail.image_url = payload.image_url
    cocktail.items.clear()
    for item in payload.items:
        recipe_item = models.RecipeItem(
            quantity=item.quantity,
            unit=item.unit,
            ingredient_id=item.ingredient_id
        )
        cocktail.items.append(recipe_item)
    db.commit()
    db.refresh(cocktail)
    return cocktail


@app.delete("/cocktails/{cocktail_id}", status_code=204)
def delete_cocktail(cocktail_id: int, db: Session = Depends(get_db)):
    cocktail = db.query(models.Cocktail).filter(models.Cocktail.id == cocktail_id).first()
    if not cocktail:
        raise HTTPException(status_code=404, detail="Cocktail not found")
    db.delete(cocktail)
    db.commit()
    return None

@app.get("/ingredients", response_model=list[schemas.Ingredient])
def list_ingredients(
    kind: schemas.IngredientKind | None = Query(default=None),
    q: str | None = Query(default=None, min_length=1, max_length=50),
    db: Session = Depends(get_db)
):
    query = db.query(models.Ingredient)
    if kind:
        query = query.filter(models.Ingredient.kind == kind)

    if q:
        query = query.filter(models.Ingredient.name.ilike(f"%{q}%"))

    ingredients = query.order_by(models.Ingredient.name).all()
    return ingredients


@app.get("/ingredients/{ingredient_id}", response_model=schemas.Ingredient)
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@app.post("/ingredients", response_model=schemas.Ingredient, status_code=201)
def create_ingredient(payload: schemas.IngredientCreate, db: Session = Depends(get_db)):
    exists = db.query(models.Ingredient).filter(models.Ingredient.name == payload.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Ingredient with this name already exists")
    ingredient = models.Ingredient(**payload.model_dump())
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


@app.put("/ingredients/{ingredient_id}", response_model=schemas.Ingredient)
def update_ingredient(ingredient_id: int, payload: schemas.IngredientCreate, db: Session = Depends(get_db)):
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    clash = db.query(models.Ingredient).filter(models.Ingredient.name == payload.name, models.Ingredient.id != ingredient_id).first()
    if clash:
        raise HTTPException(status_code=400, detail="Ingredient with this name already exists")
    for key, value in payload.model_dump().items():
        setattr(ingredient, key, value)
    db.commit()
    db.refresh(ingredient)
    return ingredient


@app.delete("/ingredients/{ingredient_id}", status_code=204)
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    used = db.query(models.RecipeItem).filter(models.RecipeItem.ingredient_id == ingredient_id).count()
    if used > 0:
        raise HTTPException(status_code=400, detail="Ingredient is still used in recipes")
    db.delete(ingredient)
    db.commit()
    return None
