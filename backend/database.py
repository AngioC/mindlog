import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Legge l'URL dalle variabili d'ambiente.
# Sostituisci la stringa di default con la tua connessione Postgres locale!
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:developer05@localhost:5432/mindlog"
)

# Niente check_same_thread, Postgres gestisce le connessioni in modo nativo
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()