from fastapi import FastAPI
from fastapi.params import Depends
from fastapi.middleware.cors import CORSMiddleware

from src.server.routes.elections import router as ElectionsRouter
from src.server.routes.statistics import router as StatisticsRouter
from src.server.routes.database import router as DatabaseRouter

# Create FastAPI app
app = FastAPI()

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
    return {"message": "Server is running"}