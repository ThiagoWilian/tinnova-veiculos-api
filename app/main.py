from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.errors import register_exception_handlers

app = FastAPI(
    title="Tinnova Veiculos API",
    version="1.0.0",
    description="API REST para gerenciamento de veiculos com JWT, RBAC e cotacao USD/BRL.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra os handlers de exceção
register_exception_handlers(app)

@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"message": "tinnova-veiculos-api is running"}

@app.get("/health", include_in_schema=False)
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router)