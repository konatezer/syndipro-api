# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router

# Crée l'application FastAPI
app = FastAPI(
    title="SyndiPro API",
    description="API de gestion de copropriétés au Québec",
    version="0.1.0"
)

# Configure CORS (permet au frontend d'appeler l'API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL du frontend Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistre les routes
app.include_router(auth_router)


@app.get("/")
def root():
    """Health check — vérifie que l'API fonctionne"""
    return {"status": "ok", "app": "SyndiPro API", "version": "0.1.0"}