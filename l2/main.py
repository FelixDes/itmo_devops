import os
import socket

import psycopg
from fastapi import FastAPI, Response
from pydantic import BaseModel

app = FastAPI()


class Note(BaseModel):
    text: str


def connect():
    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=3,
    )


@app.get("/")
def index():
    with connect() as conn:
        rows = conn.execute("SELECT id, text FROM notes").fetchall()
    return {"host": socket.gethostname(), "notes": [{"id": i, "text": t} for i, t in rows]}


@app.post("/notes")
def add_note(note: Note):
    with connect() as conn:
        conn.execute("INSERT INTO notes (text) VALUES (%s)", (note.text,))
    return {"ok": True}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz(response: Response):
    try:
        with connect() as conn:
            conn.execute("SELECT 1 FROM notes")
    except psycopg.Error:
        response.status_code = 503
        return {"status": "unavailable"}
    return {"status": "ok"}
