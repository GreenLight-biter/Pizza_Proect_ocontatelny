from sqlalchemy.orm import Session
from fastapi import HTTPException

from database import PizzaDB, RestoranDB, ChefDB, ReviewDB, IngredientDB
from models import Pizza, SostavPizza, Ingredient, Restoran, PizzaUpdate, Review


def pizza_db_to_pydantic(pizza_db: PizzaDB) -> Pizza:
    return Pizza(
        name=pizza_db.name,
        cheese=pizza_db.cheese,
        dough=pizza_db.dough,
        sastav=SostavPizza(
            ingredients=[Ingredient(name=ing.name) for ing in pizza_db.ingredients]
        ),
        secret_ingr=pizza_db.secret_ingr,
        restaurant=Restoran(
            name=pizza_db.restaurant.name,
            adres=pizza_db.restaurant.adres
        )
    )


def get_or_create_ingredient(db: Session, ingredient_name: str) -> IngredientDB:
    ingredient = db.query(IngredientDB).filter(
        IngredientDB.name == ingredient_name
    ).first()
    
    if not ingredient:
        ingredient = IngredientDB(name=ingredient_name)
        db.add(ingredient)
        db.commit()
        db.refresh(ingredient)
    
    return ingredient


def get_all_pizzas(db: Session):
    pizzas = db.query(PizzaDB).all()
    return [pizza_db_to_pydantic(p) for p in pizzas]


def create_new_pizza(db: Session, pizza: Pizza):
    restaurant = db.query(RestoranDB).filter(
        RestoranDB.name == pizza.restaurant.name
    ).first()
    
    if not restaurant:
        restaurant = RestoranDB(
            name=pizza.restaurant.name,
            adres=pizza.restaurant.adres
        )
        db.add(restaurant)
        db.commit()
        db.refresh(restaurant)
    
    new_pizza = PizzaDB(
        name=pizza.name,
        cheese=pizza.cheese,
        dough=pizza.dough,
        secret_ingr=pizza.secret_ingr,
        restaurant_id=restaurant.id
    )
    
    for ingredient in pizza.sastav.ingredients:
        ingredient_db = get_or_create_ingredient(db, ingredient.name)
        new_pizza.ingredients.append(ingredient_db)
    
    db.add(new_pizza)
    db.commit()
    
    total_pizzas = db.query(PizzaDB).count()
    return {"message": "Добавлено", "total_pizzas": total_pizzas}


def create_new_restoran(db: Session, restoran: Restoran):
    new_restoran = RestoranDB(name=restoran.name, adres=restoran.adres)
    db.add(new_restoran)
    db.commit()
    
    total_restorans = db.query(RestoranDB).count()
    return {"message": "Ресторан добавлен", "total_restorans": total_restorans}


def create_new_chef(db: Session, chef):
    restaurant = db.query(RestoranDB).filter(
        RestoranDB.name == chef.chefs_restoran.name
    ).first()
    
    if not restaurant:
        raise HTTPException(status_code=404, detail="Ресторан не найден")
    
    new_chef = ChefDB(
        name_chef=chef.name_chef,
        restaurant_id=restaurant.id
    )
    db.add(new_chef)
    db.commit()
    
    total_chefs = db.query(ChefDB).count()
    return {"message": "Шеф-повар добавлен", "total_chefs": total_chefs}


def create_new_review(db: Session, review: Review):
    restaurant = db.query(RestoranDB).filter(
        RestoranDB.name == review.restaurant.name
    ).first()
    
    if not restaurant:
        raise HTTPException(status_code=404, detail="Ресторан не найден")
    
    new_review = ReviewDB(
        restaurant_id=restaurant.id,
        rating=review.rating,
        review_text=review.review_text
    )
    db.add(new_review)
    db.commit()
    
    total_reviews = db.query(ReviewDB).count()
    return {"message": "Отзыв добавлен", "total_reviews": total_reviews}


def add_ingredient_to_pizza_service(db: Session, pizza_id: int, ingredient_name: str):
    pizza = db.query(PizzaDB).filter(PizzaDB.id == pizza_id).first()
    
    if not pizza:
        raise HTTPException(status_code=404, detail="Пицца не найдена")
    
    existing_ingredient = next(
        (ing for ing in pizza.ingredients if ing.name == ingredient_name),
        None
    )
    
    if not existing_ingredient:
        ingredient_db = get_or_create_ingredient(db, ingredient_name)
        pizza.ingredients.append(ingredient_db)
        db.commit()
        return {
            "message": "Ингредиент добавлен",
            "pizza": pizza.name,
            "ingredients": [ing.name for ing in pizza.ingredients]
        }
    else:
        return {
            "message": "Ингредиент уже есть в пицце",
            "pizza": pizza.name
        }


def update_pizza_full_service(db: Session, pizza_id: int, pizza: Pizza):
    pizza_db = db.query(PizzaDB).filter(PizzaDB.id == pizza_id).first()
    
    if not pizza_db:
        raise HTTPException(status_code=404, detail="Пицца не найдена")
    
    restaurant = db.query(RestoranDB).filter(
        RestoranDB.name == pizza.restaurant.name
    ).first()
    
    if not restaurant:
        restaurant = RestoranDB(
            name=pizza.restaurant.name,
            adres=pizza.restaurant.adres
        )
        db.add(restaurant)
        db.commit()
        db.refresh(restaurant)
    
    pizza_db.name = pizza.name
    pizza_db.cheese = pizza.cheese
    pizza_db.dough = pizza.dough
    pizza_db.secret_ingr = pizza.secret_ingr
    pizza_db.restaurant_id = restaurant.id
    
    pizza_db.ingredients.clear()
    for ingredient in pizza.sastav.ingredients:
        ingredient_db = get_or_create_ingredient(db, ingredient.name)
        pizza_db.ingredients.append(ingredient_db)
    
    db.commit()
    db.refresh(pizza_db)
    
    return pizza_db_to_pydantic(pizza_db)


def update_pizza_partial_service(db: Session, pizza_id: int, pizza_update: PizzaUpdate):
    pizza_db = db.query(PizzaDB).filter(PizzaDB.id == pizza_id).first()
    
    if not pizza_db:
        raise HTTPException(status_code=404, detail="Пицца не найдена")
    
    update_data = pizza_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "sastav" and value is not None:
            pizza_db.ingredients.clear()
            for ingredient in value.ingredients:
                ingredient_db = get_or_create_ingredient(db, ingredient.name)
                pizza_db.ingredients.append(ingredient_db)
        elif field == "restaurant" and value is not None:
            restaurant = db.query(RestoranDB).filter(
                RestoranDB.name == value.name
            ).first()
            if restaurant:
                pizza_db.restaurant_id = restaurant.id
        elif field not in ["sastav", "restaurant"]:
            setattr(pizza_db, field, value)
    
    db.commit()
    db.refresh(pizza_db)
    
    return pizza_db_to_pydantic(pizza_db)


def delete_pizza_service(db: Session, pizza_id: int):
    pizza = db.query(PizzaDB).filter(PizzaDB.id == pizza_id).first()
    
    if not pizza:
        raise HTTPException(status_code=404, detail="Пицца не найдена")
    
    pizza_name = pizza.name
    db.delete(pizza)
    db.commit()
    
    total_pizzas = db.query(PizzaDB).count()
    return {
        "message": "Пицца удалена",
        "deleted_pizza": pizza_name,
        "total_pizzas": total_pizzas
    }


def get_restaurant_menu_service(db: Session, restaurant_id: int):
    restaurant = db.query(RestoranDB).filter(RestoranDB.id == restaurant_id).first()
    
    if not restaurant:
        raise HTTPException(status_code=404, detail="Ресторан не найден")
    
    restaurant_pizzas = db.query(PizzaDB).filter(
        PizzaDB.restaurant_id == restaurant_id
    ).all()
    
    return {
        "restaurant": Restoran(name=restaurant.name, adres=restaurant.adres),
        "menu": [pizza_db_to_pydantic(p) for p in restaurant_pizzas],
        "total_pizzas": len(restaurant_pizzas)
    }