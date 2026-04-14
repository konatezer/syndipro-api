# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.assemblees import router as assemblees_router
from app.api.auth import router as auth_router
from app.api.communications import router as communications_router
from app.api.finances import router as finances_router
from app.api.maintenance import router as maintenance_router
from app.api.membres import router as membres_router
from app.api.syndicats import router as syndicats_router
from app.api.unites import router as unites_router

# Crée l'application FastAPI
app = FastAPI(
    title="SyndiPro API",
    description="API de gestion de copropriétés au Québec",
    version="0.6.0",
)

# Configure CORS (permet au frontend d'appeler l'API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistre les routes
app.include_router(auth_router)
app.include_router(syndicats_router)
app.include_router(unites_router)
app.include_router(membres_router)
app.include_router(finances_router)
app.include_router(assemblees_router)
app.include_router(maintenance_router)
app.include_router(communications_router)


@app.get("/")
def root():
    """Health check — vérifie que l'API fonctionne"""
    return {"status": "ok", "app": "SyndiPro API", "version": "0.6.0"}
