from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <- 1. Importa il middleware
import models
from database import engine
from routers import auth, entries, tags, stats_ai, habits, medications

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MindLog API")

# --- 2. AGGIUNGI LA CONFIGURAZIONE CORS QUI ---
# Questo dice a FastAPI di accettare richieste da qualsiasi dominio, 
# con qualsiasi metodo (incluso OPTIONS) e qualsiasi intestazione.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Consente le chiamate da qualsiasi porta/sito locale
    allow_credentials=True,
    allow_methods=["*"], # Risolve il problema del 405 sbloccando le chiamate OPTIONS
    allow_headers=["*"],
)
# ----------------------------------------------

app.include_router(auth.router)
app.include_router(entries.router)
app.include_router(stats_ai.router)
app.include_router(tags.router)
app.include_router(habits.router)
app.include_router(medications.router)

@app.get("/", tags=["Health"])
def read_root():
    return {"status": "ok", "message": "Benvenuto in MindLog API!"}