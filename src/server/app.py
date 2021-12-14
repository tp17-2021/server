import os

from fastapi import FastAPI
from fastapi.params import Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.server.routes.elections import router as ElectionsRouter
from src.server.routes.statistics import router as StatisticsRouter
from src.server.routes.database import router as DatabaseRouter
# from server.routes.elections import router as ElectionsRouter
# from server.routes.statistics import router as StatisticsRouter
# from server.routes.database import router as DatabaseRouter

# Create FastAPI app
app = FastAPI()

# create public accesible folder if not exists
folder_path = "src/server/public"
if not os.path.exists(folder_path):
    os.mkdir(folder_path)

# Mount public accesible folder for assets and downloadable files
# /public/{any path} with be with src/server/public/{any path}
app.mount("/public", StaticFiles(directory="src/server/public"), name="public")

# Add Middleware
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ElectionsRouter)
app.include_router(StatisticsRouter)
app.include_router(DatabaseRouter)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Server is running"
    }