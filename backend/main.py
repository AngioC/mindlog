from fastapi import FastAPI
import models
from database import engine

# Importiamo anche 'tags'
from routers import auth, entries, tags

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MindLog API")

# Includiamo i tre router
app.include_router(auth.router)
app.include_router(entries.router)
app.include_router(tags.router)

@app.get("/", tags=["Health"])
def read_root():
    return {"status": "ok", "message": "Benvenuto in MindLog API!"}