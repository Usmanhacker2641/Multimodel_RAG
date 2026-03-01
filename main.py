from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api_routes import upload_routes, query_routes, history_routes, feedback_routes, model_routes

app = FastAPI(title="RAG Multi-LLM Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_routes.router)
app.include_router(query_routes.router)
app.include_router(history_routes.router)
app.include_router(feedback_routes.router)
app.include_router(model_routes.router)


@app.get("/")
def home():
    return {"message": "RAG Multi-LLM API running ✅"}