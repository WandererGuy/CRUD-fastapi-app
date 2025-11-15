from fastapi import FastAPI
# ---------- Initialize ----------
app = FastAPI(title="Brand CRUD API (Class-Based)")




from routes.v1.brand import router as brand_router
app.include_router(brand_router)
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)