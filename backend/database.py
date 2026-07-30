import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Carica le variabili dal file .env
load_dotenv()

# Prendi l'URL in modo sicuro (se non c'è, darà errore invece di esporre dati)
DATABASE_URL = os.environ.get("DATABASE_URL")

# Crea il motore di connessione
engine = create_engine(DATABASE_URL)

# Questa "fabbrica" creerà le sessioni per dialogare col DB in ogni rotta API
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()