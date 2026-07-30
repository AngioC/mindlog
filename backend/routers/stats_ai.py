import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract
from groq import Groq

from models import Entry, User
from database import get_db
from dependencies import get_current_user

# Inizializza il client Groq leggendo la chiave GROQ_API_KEY dalle variabili d'ambiente
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

router = APIRouter()

@router.get("/stats/ai-summary")
def get_ai_monthly_summary(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    now = datetime.now()
    
    # 1. Recuperiamo tutte le note dell'utente per il mese e anno corrente
    entries = db.query(Entry).filter(
        Entry.user_id == current_user.id,
        extract('month', Entry.entry_date) == now.month,
        extract('year', Entry.entry_date) == now.year
    ).all()

    if len(entries) < 3:
        raise HTTPException(
            status_code=400, 
            detail="Servono almeno 3 pensieri in questo mese per generare un resoconto intelligente."
        )

    # 2. Prepariamo il testo delle note
    notes_text = ""
    for e in entries:
        title_str = f" - Titolo: {e.title}" if e.title else ""
        mood_str = f" (Umore: {e.mood_score}/5)" if e.mood_score else ""
        notes_text += f"\nData {e.entry_date}{title_str}{mood_str}:\n{e.content}\n---"

    # 3. Prompt strutturato per Groq
    prompt = f"""
    Sei un assistente empatico e analitico di un diario personale.
    Analizza i seguenti pensieri scritti dall'utente nel mese corrente e fornisci un resoconto strutturato.

    Pensieri del mese:
    {notes_text}

    Rispondi TASSATIVAMENTE ed ESCLUSIVAMENTE con un oggetto JSON valido in lingua italiana con questa struttura:
    {{
      "highlights": ["punto o momento chiave 1", "punto o momento chiave 2"],
      "recurring_themes": ["tema 1", "tema 2"],
      "advice": "Un consiglio empatico e motivazionale di 2-3 frasi per il prossimo mese."
    }}
    """

    try:
        # Chiamata a Groq usando Llama 3.3 70B
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Sei un assistente che risponde esclusivamente in formato JSON valido."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.6,
        )
        
        # Restituiamo il contenuto JSON
        return response.choices[0].message.content

    except Exception as e:
        print("Errore Groq:", e)
        raise HTTPException(
            status_code=500, 
            detail="Errore durante la generazione del resoconto AI con Groq."
        )