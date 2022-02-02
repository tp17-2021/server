import os

from fastapi import FastAPI
from fastapi.params import Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.server.routes.database import router as DatabaseRouter
from src.server.routes.elections import router as ElectionsRouter
from src.server.routes.encryption import router as EncryptionRouter
from src.server.routes.statistics import router as StatisticsRouter

# Create FastAPI app
app = FastAPI(root_path=os.environ['ROOT_PATH'])

# moze sa to hodit do buducna (exporty...)
# # Create public accesible folder if not exists
# folder_path = "src/server/public"
# if not os.path.exists(folder_path):
#     os.mkdir(folder_path)

# # Mount public accesible folder for assets and downloadable files
# # /public/{any path} with be with src/server/public/{any path}
# app.mount("/public", StaticFiles(directory="src/server/public"), name="public")

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
app.include_router(EncryptionRouter)
app.include_router(StatisticsRouter)


@app.get("/", tags=["Root"])
def root():
    content = {
        "status": "success",
        "message": "Server is running"
    }
    return content