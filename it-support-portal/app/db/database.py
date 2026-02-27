from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

<<<<<<< HEAD:it-support-portal/app/db/database.py
SQLALCHEMY_DATABASE_URL = "sqlite:///./app/db/portal.db"
=======
SQLALCHEMY_DATABASE_URL = "sqlite:///./mainDatabase.db"
>>>>>>> refs/remotes/origin/main:it-support-portal/database.py

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()