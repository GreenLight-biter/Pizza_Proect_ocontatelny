from pydantic import BaseModel
from typing import List, Optional

class Ingredient(BaseModel):
    name: str
    
    class Config:
        from_attributes = True


class Restoran(BaseModel):
    name: str
    adres: str
    
    class Config:
        from_attributes = True


class Chef(BaseModel):
    name_chef: str
    chefs_restoran: Restoran
    
    class Config:
        from_attributes = True


class SostavPizza(BaseModel):
    ingredients: List[Ingredient]


class Pizza(BaseModel):
    name: str
    cheese: str
    dough: str
    sastav: SostavPizza
    secret_ingr: str
    restaurant: Restoran
    
    class Config:
        from_attributes = True


class PizzaUpdate(BaseModel):
    name: Optional[str] = None
    cheese: Optional[str] = None
    dough: Optional[str] = None
    sastav: Optional[SostavPizza] = None
    secret_ingr: Optional[str] = None
    restaurant: Optional[Restoran] = None


class Review(BaseModel):
    restaurant: Restoran
    rating: int
    review_text: str
    
    class Config:
        from_attributes = True