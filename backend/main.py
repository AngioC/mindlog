from fastapi import FastAPI
import models
from database import engine
from routers import auth, entries

# Genera le tabelle sul database se non esistono
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MindLog API")

# Includiamo i nostri moduli separati
app.include_router(auth.router)
app.include_router(entries.router)

# Una rotta base di cortesia per verificare che il server sia su
@app.get("/", tags=["Health"])
def read_root():
    return {"status": "ok", "message": "Benvenuto in MindLog API!"}