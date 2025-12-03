from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


DATABASE_URL = "postgresql://postgres:123@localhost:5432/Datapizza"


engine = create_engine(DATABASE_URL, echo=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


pizza_ingredients = Table(
    'pizza_ingredients',
    Base.metadata,
    Column('pizza_id', Integer, ForeignKey('pizzas.id', ondelete='CASCADE'), primary_key=True),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id', ondelete='CASCADE'), primary_key=True)
)



class RestoranDB(Base):
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    adres = Column(String(255), nullable=False)
    
    
    chefs = relationship("ChefDB", back_populates="restaurant", cascade="all, delete-orphan")
    pizzas = relationship("PizzaDB", back_populates="restaurant", cascade="all, delete-orphan")
    reviews = relationship("ReviewDB", back_populates="restaurant", cascade="all, delete-orphan")



class ChefDB(Base):
    __tablename__ = "chefs"
    
    id = Column(Integer, primary_key=True, index=True)
    name_chef = Column(String(255), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    
    
    restaurant = relationship("RestoranDB", back_populates="chefs")



class IngredientDB(Base):
    __tablename__ = "ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    
    
    pizzas = relationship("PizzaDB", secondary=pizza_ingredients, back_populates="ingredients")



class PizzaDB(Base):
    __tablename__ = "pizzas"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    cheese = Column(String(255), nullable=False)
    dough = Column(String(100), nullable=False)
    secret_ingr = Column(String(255), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    
    
    restaurant = relationship("RestoranDB", back_populates="pizzas")
    ingredients = relationship("IngredientDB", secondary=pizza_ingredients, back_populates="pizzas")



class ReviewDB(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    review_text = Column(Text)
    
    
    restaurant = relationship("RestoranDB", back_populates="reviews")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы успешно созданы!")


if __name__ == "__main__":
    create_tables()