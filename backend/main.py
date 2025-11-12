import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from env import PORT
from router.processURL import process_router, initialize_component
from router.auth_routes import auth_router
from router.user_routes import user_router
from database.postgresdb import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Server startup: Initializing components...")
    db_session = next(get_db())
    app.state.db_session = db_session
    initialize_component()
    print("Server startup: Initialization complete.")
    yield
    # Code to run on shutdown (if any)
    print("Server shutdown.")


app = FastAPI(lifespan=lifespan)

#--- Include Routers ---
app.include_router(process_router)
app.include_router(auth_router)
app.include_router(user_router)

@app.get("/")
async def root():
    return {"Body": "Welcome to real estate API"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=int(PORT))

