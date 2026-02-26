
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, books, recommendations


# Create FastAPI application instance
app = FastAPI(title="LuminaLib API")


# Enable CORS for frontend communication

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register domain routers
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(recommendations.router)


# Basic liveness check
@app.get("/health")
def health():
    return {"status": "ok"}


# Check Ollama  and model status
@app.get("/health/ollama")
async def health_ollama():
    from app.config import settings

    # Skip if Ollama is not the active LLM provider
    if settings.llm_provider != "ollama":
        return {
            "ollama": "not_used",
            "llm_provider": settings.llm_provider
        }

    import httpx

    base = settings.ollama_base_url.rstrip("/")
    model = getattr(settings, "ollama_model", "llama3.2") or "llama3.2"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{base}/api/tags")
            r.raise_for_status()
            data = r.json()

        # Extract available model names
        models = data.get("models") or []
        names = [m.get("name", "") for m in models]

        # Validate configured model is loaded
        model_loaded = any(
            name == model or name.startswith(model + ":")
            for name in names
        )

        return {
            "ollama": "ok",
            "url": base,
            "model": model,
            "model_loaded": model_loaded,
            "hint": "Run: ollama pull " + model if not model_loaded else None,
        }

    except Exception as e:
        # Return diagnostic info if Ollama is unreachable
        return {
            "ollama": "unavailable",
            "url": base,
            "model": model,
            "detail": str(e),
        }