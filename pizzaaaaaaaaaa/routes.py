from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from database import get_db, RestoranDB, ChefDB, PizzaDB, ReviewDB, IngredientDB
from models import Ingredient, Restoran, Chef, Pizza, PizzaUpdate, Review
from services import (
    get_all_pizzas,
    create_new_pizza,
    create_new_restoran,
    create_new_chef,
    create_new_review,
    add_ingredient_to_pizza_service,
    update_pizza_full_service,
    update_pizza_partial_service,
    delete_pizza_service,
    get_restaurant_menu_service
)

router = APIRouter()

@router.get("/restorany_AlmurtAta", response_model=List[Restoran])
async def restorany(db: Session = Depends(get_db)):
    restorans = db.query(RestoranDB).all()
    return restorans


@router.get("/chefs", response_model=List[Chef])
async def chefi(db: Session = Depends(get_db)):
    chefs = db.query(ChefDB).all()
    return chefs


@router.get("/pizzas", response_model=List[Pizza])
async def pizzaq(db: Session = Depends(get_db)):
    return get_all_pizzas(db)


@router.get("/reviews", response_model=List[Review])
async def get_reviews(db: Session = Depends(get_db)):
    reviews = db.query(ReviewDB).all()
    return reviews


@router.get("/ingredients", response_model=List[Ingredient])
async def get_ingredients(db: Session = Depends(get_db)):
    ingredients = db.query(IngredientDB).all()
    return ingredients


@router.post("/pizza/post")
async def pizzaplus(pizza: Pizza, db: Session = Depends(get_db)):
    return create_new_pizza(db, pizza)


@router.post("/restoran/post")
async def add_restoran(restoran: Restoran, db: Session = Depends(get_db)):
    return create_new_restoran(db, restoran)


@router.post("/chef/post")
async def add_chef(chef: Chef, db: Session = Depends(get_db)):
    return create_new_chef(db, chef)


@router.post("/review/post")
async def add_review(review: Review, db: Session = Depends(get_db)):
    return create_new_review(db, review)


@router.post("/ingredient/post")
async def add_ingredient_to_pizza(pizza_id: int, ingredient_name: str, db: Session = Depends(get_db)):
    return add_ingredient_to_pizza_service(db, pizza_id, ingredient_name)


@router.put("/pizza/{pizza_id}", response_model=Pizza)
async def update_pizza_full(pizza_id: int, pizza: Pizza, db: Session = Depends(get_db)):
    return update_pizza_full_service(db, pizza_id, pizza)


@router.patch("/pizza/{pizza_id}", response_model=Pizza)
async def update_pizza_partial(pizza_id: int, pizza_update: PizzaUpdate, db: Session = Depends(get_db)):
    return update_pizza_partial_service(db, pizza_id, pizza_update)


@router.delete("/pizza/{pizza_id}")
async def delete_pizza(pizza_id: int, db: Session = Depends(get_db)):
    return delete_pizza_service(db, pizza_id)


@router.get("/restaurants/{restaurant_id}/menu/")
async def get_restaurant_menu(restaurant_id: int, db: Session = Depends(get_db)):
    return get_restaurant_menu_service(db, restaurant_id)