from typing import Literal, Optional

from pydantic import BaseModel, Field

IngredientKind = Literal["base", "liqueur", "juice", "syrup", "bitter", "garnish", "other"]
Unit = Literal["ml", "oz", "tsp", "tbsp", "dash", "piece"]


class IngredientBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    kind: IngredientKind = "other"


class IngredientCreate(IngredientBase):
    pass


class Ingredient(IngredientBase):
    id: int
    model_config = {"from_attributes": True}


class RecipeItemBase(BaseModel):
    quantity: float = Field(gt=0, le=5000)
    unit: Unit = "ml"


class RecipeItemCreate(RecipeItemBase):
    ingredient_id: int


class RecipeItem(RecipeItemBase):
    id: int
    ingredient: Ingredient
    model_config = {"from_attributes": True}


class CocktailBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    instructions: str = Field(min_length=1)
    glass: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None


class CocktailCreate(CocktailBase):
    items: list[RecipeItemCreate] = []


class Cocktail(CocktailBase):
    id: int
    items: list[RecipeItem] = []
    model_config = {"from_attributes": True}
