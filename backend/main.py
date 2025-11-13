from fastapi import FastAPI
from contextlib import asynccontextmanager
from router.processURL import process_router, initialize_component
from router.user_routes import user_router
from database.postgresdb import engine
from models import user_model
from middlewares.error_middleware import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Server startup: Initializing components...")
    
    print("Creating database tables...📑")
    user_model.Base.metadata.create_all(bind=engine)
    print("Database tables created.✅")
    initialize_component()
    print("Server startup: Initialization complete.")
    yield
    # Code to run on shutdown (if any)
    print("Server shutdown.")

app = FastAPI(lifespan=lifespan)
setup_exception_handlers(app)

#--- Include Routers ---
app.include_router(process_router)
app.include_router(user_router)

@app.get("/")
async def root():
    return {"Body": "Welcome to real estate API"}
