import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from bson import ObjectId
from database import init_db
from fastapi import FastAPI, HTTPException, Query
from fastapi._compat import shared
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from routes.analysis import router as analysis_router
from routes.contracts import router as contracts_router

app = FastAPI(
    title="vakeel-contract-api",
    description="AI Powered Contract Analysis using Gemini",
    version="1.0.0",
    # lifespan=lifespan,
)

@app.on_event("startup")
async def startup_event():
    init_db()

app.include_router(contracts_router)
app.include_router(analysis_router)

# def get_contracts_collection():
#     return db.contracts


@app.get("/")
async def root():
    return {
        "message": "Hello from vakeel-contract-api!",
        "version": app.version,
        "endpoints": [
            {"path": route.path, "name": route.name, "methods": list(route.methods)}
            for route in app.router.routes
        ]
    }


@app.get("/health")
async def health_check():
    try:
        await client.admin.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")


# def main():
#     print("Hello from vakeel-contract-api!")


# if __name__ == "__main__":
#     main()
