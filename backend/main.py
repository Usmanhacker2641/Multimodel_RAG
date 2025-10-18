from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import backend.feedback_routes as feedback_routes
import backend.history_routes as history_routes
import backend.model_routes as model_routes
import backend.query_routes as query_routes
import backend.upload_routers as upload_routes
import uvicorn
from time import perf_counter
from uuid import uuid4
from core.logger import setup_logger

logger = setup_logger()

app = FastAPI(
    title="RAG Multi-LLM Backend",
    description="Backend API for RAG system with multiple LLM support",
    version="1.0.0"
)


@app.on_event("startup")
async def on_startup():
    """Log summary metadata when the service starts."""
    logger.info("Backend startup complete (routes=%d)", len(app.routes))


@app.on_event("shutdown")
async def on_shutdown():
    """Log when the service is shutting down."""
    logger.info("Backend shutdown complete")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    client_host = request.client.host if request.client else "unknown"
    path = request.url.path
    start = perf_counter()
    logger.info(
        "Request start method=%s path=%s client=%s request_id=%s",
        request.method,
        path,
        client_host,
        request_id,
    )

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled error while processing method=%s path=%s request_id=%s",
            request.method,
            path,
            request_id,
        )
        raise

    duration_ms = (perf_counter() - start) * 1000
    logger.info(
        "Request end method=%s path=%s status=%s duration_ms=%.2f request_id=%s",
        request.method,
        path,
        response.status_code,
        duration_ms,
        request_id,
    )
    response.headers["X-Process-Time-ms"] = f"{duration_ms:.2f}"
    response.headers.setdefault("X-Request-ID", request_id)
    return response


# Allow frontend (Streamlit) access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routes
app.include_router(upload_routes.router, prefix="/api", tags=["upload"])
app.include_router(query_routes.router, prefix="/api", tags=["query"])
app.include_router(history_routes.router, prefix="/api", tags=["history"])
app.include_router(feedback_routes.router, prefix="/api", tags=["feedback"])
app.include_router(model_routes.router, prefix="/api", tags=["models"])


@app.get("/")
def home():
    return {"message": "RAG Multi-LLM API running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    logger.info("Starting backend server...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
