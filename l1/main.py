import os
import socket
import sqlite3

from fastapi import FastAPI
from pydantic import BaseModel

DATA_DIR = os.getenv("DATA_DIR", ".")
os.makedirs(DATA_DIR, exist_ok=True)
db = sqlite3.connect(os.path.join(DATA_DIR, "notes.db"), check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, text TEXT NOT NULL)")

app = FastAPI()


class Note(BaseModel):
    text: str


@app.get("/")
def index():
    rows = db.execute("SELECT id, text FROM notes").fetchall()
    return {"host": socket.gethostname(), "notes": [{"id": i, "text": t} for i, t in rows]}


@app.post("/notes")
def add_note(note: Note):
    with db:
        db.execute("INSERT INTO notes (text) VALUES (?)", (note.text,))
    return {"ok": True}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
