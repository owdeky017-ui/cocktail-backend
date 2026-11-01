from sqlalchemy import Column, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Cocktail(Base):
    __tablename__ = "cocktails"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    instructions = Column(String, nullable=False)
    glass = Column(String)
    category = Column(String, index=True)
    image_url = Column(String)

    items = relationship("RecipeItem", back_populates="cocktail", cascade="all, delete-orphan")

  
class RecipeItem(Base):
    __tablename__ = "recipe_items"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Float, nullable=False)
    cocktail_id = Column(Integer, ForeignKey("cocktails.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    unit = Column(String, nullable=False, default="ml")

    cocktail = relationship("Cocktail", back_populates="items")
    ingredient = relationship("Ingredient", back_populates="items")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    kind = Column(String, index=True, nullable=False, default="other")

    items = relationship("RecipeItem", back_populates="ingredient")
    