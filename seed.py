# seed.py

from sqlalchemy.orm import sessionmaker, Session
from data.tea_data import teas_list
from config.environment import db_URI
from sqlalchemy import create_engine
from models.tea import Base, TeaModel

engine = create_engine(db_URI)
SessionLocal = sessionmaker(bind=engine)

# This seed file is a separate program that can be used to "seed" our database with some initial data.
try:
    print("Recreating database...")
    # Dropping (or deleting) the tables and creating them again is for convenience. Once we start to play around with
    # our data, changing our models, this seed program will allow us to rapidly throw out the old data and replace it.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("seeding the database...")
    # Seed teas
    db = SessionLocal()
    db.add_all(teas_list)
    db.commit()
    db.close()

    print("Database seeding complete! 👋")
except Exception as e:
    print("An error occurred:", e)
