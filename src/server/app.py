import os

from fastapi import FastAPI
from fastapi.params import Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.server.routes.database import router as DatabaseRouter
from src.server.routes.elections import router as ElectionsRouter
from src.server.routes.encryption import router as EncryptionRouter
from src.server.routes.statistics import router as StatisticsRouter

from src.server.database import connect_to_mongo

# Create FastAPI app
app = FastAPI(root_path=os.environ['ROOT_PATH'])

# Add Middleware
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
# import asyncio
    await connect_to_mongo()

# Include routes
app.include_router(DatabaseRouter)
app.include_router(ElectionsRouter)
app.include_router(EncryptionRouter)
app.include_router(StatisticsRouter)


@app.get("/", tags=["Root"])
def root():
    content = {
        "status": "success",
        "message": "Server is running"
    }
    return content