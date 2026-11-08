FROM python:3.13-slim-trixie AS builder

COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim-trixie

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data

RUN useradd --system --uid 10001 app \
    && mkdir /data \
    && chown app /data

COPY --from=builder /opt/venv /opt/venv
WORKDIR /srv
COPY main.py .

USER app
EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz')"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
