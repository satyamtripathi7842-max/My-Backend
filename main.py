"""
main.py
SentinelX-AI backend entrypoint. Run with:
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
import auth
from agents import supplier_agent, alerts_router, simulate_router

app = FastAPI(title="SentinelX-AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth.router)
app.include_router(supplier_agent.router)
app.include_router(alerts_router.router)
app.include_router(simulate_router.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "SentinelX-AI backend"}


@app.get("/health")
def health():
    return {"status": "healthy"}
