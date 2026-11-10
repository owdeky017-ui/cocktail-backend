from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from fastapi.middleware.cors import CORSMiddleware

import models
import schemas
import mixology
from database import Base, engine, get_db, SessionLocal


Base.metadata.create_all(bind=engine)


app = FastAPI(title="Cocktail App", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    try:
        if db.query(models.Cocktail).count() > 0:
            return

        ingredients = {
             "Gin": "base",
            "Vodka": "base",
            "Campari": "liqueur",
            "Sweet Vermouth": "liqueur",
            "Lemon juice": "juice",
            "Syrup": "syrup",
            "Soda water": "other",
            "Tonic Water": "other"
        }
        for name, kind in ingredients.items():
            db.add(models.Ingredient(name=name, kind=kind))
        db.commit()

        ids = {i.name: i.id for i in db.query(models.Ingredient).all()}

        recipes = [
            ("Negroni", "Stir with ice and strain into a rocks glass over a large cube.", "Rocks", "Classic",
             [("Gin", 30), ("Campari", 30), ("Sweet Vermouth", 30)]),
            ("Gin Tonic", "Build over ice in a highball glass and stir gently.", "Highball", "Classic",
             [("Gin", 50), ("Tonic Water", 150)]),
            ("Gin Sour", "Shake with ice and strain into a chilled coupe.", "Coupe", "Sour",
             [("Gin", 50), ("Lemon juice", 25), ("Syrup", 15)]),
            ("Vodka Soda", "Build over ice in a highball glass and stir gently.", "Highball", "Classic",
             [("Vodka", 50), ("Soda water", 150)])
        ]

        for name, instructions, glass, category, items in recipes:
            cocktail = models.Cocktail(
                name=name,
                instructions=instructions,
                glass=glass,
                category=category
            )
            for ingredient_name, quantity in items:
                cocktail.items.append(models.RecipeItem(
                    quantity=quantity,
                    unit="ml",
                    ingredient_id=ids[ingredient_name]
                ))
            db.add(cocktail)

        db.commit()
    finally:
        db.close()

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


@app.get("/suggest")
def suggest_cocktails(
    available_ingredients: list[str] = Query(..., min_length=1),
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    cocktails = db.query(models.Cocktail).options(joinedload(models.Cocktail.items).joinedload(models.RecipeItem.ingredient)).all()
    suggestions = mixology.suggest(
        cocktails=[{
            'name': cocktail.name,
            'ingredients': [item.ingredient.name for item in cocktail.items]
        } for cocktail in cocktails],
        available_ingredients=available_ingredients,
        limit=limit
    )
    ids = {cocktail.name: cocktail.id for cocktail in cocktails}
    return [{"id": ids[name], "name": name, "score": score} for name, score in suggestions]


@app.get("/cocktails/{cocktail_id}/scale")
def scale_cocktail(cocktail_id: int, servings: float = Query(default=1.0, gt=0, le=50), db: Session = Depends(get_db)):
    cocktail = db.query(models.Cocktail).options(joinedload(models.Cocktail.items).joinedload(models.RecipeItem.ingredient)).filter(models.Cocktail.id == cocktail_id).first()
    if not cocktail:
        raise HTTPException(status_code=404, detail="Cocktail not found")
    if not cocktail.items:
        raise HTTPException(status_code=400, detail="Cocktail has no ingredients to scale")

    amount  = [(f"{item.quantity:g} {item.unit}", f"{item.quantity:g} {item.unit}") for item in cocktail.items]
    scaled = mixology.scale(amount, servings)
    scaled_items = []
    for item, (amount, _) in zip(cocktail.items, scaled):
        quantity, unit = mixology.normalize_unit(amount)
        millilitres = mixology.to_ml(quantity, unit) if unit in mixology.UNIT_TO_ML else None
        scaled_items.append({
            "ingredient": item.ingredient.name,
            "amount" : amount,
            "millilitres": round(millilitres, 2) if millilitres is not None else None
        })
    return {
        "name": cocktail.name,       
        "servings": servings,
        "items": scaled_items
    }