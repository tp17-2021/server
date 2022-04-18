# General modules
import os

# FastAPI modules
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Server modules
from src.server.routes.database import router as DatabaseRouter
from src.server.routes.elastic import router as ElasticRouter
from src.server.routes.elections import router as ElectionsRouter
from src.server.routes.encryption import router as EncryptionRouter
from src.server.routes.statistics import router as StatisticsRouter
from src.server.database import connect_to_mongo

# Create FastAPI app
app = FastAPI(root_path=os.environ["ROOT_PATH"])

# Add Middleware
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(DatabaseRouter)
app.include_router(ElectionsRouter)
app.include_router(ElasticRouter)
app.include_router(EncryptionRouter)
app.include_router(StatisticsRouter)


@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()


@app.get("/", tags=["Root"])
def root():
    """ Check if server is running """
    content = {
        "status": "success",
        "message": "Server is running"
    }
    return content