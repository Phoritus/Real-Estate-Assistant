from fastapi import FastAPI
from fastapi_fortify import SecurityMiddleware
from router import auth_routes, user_routes, process_routes
from database.postgresdb import engine
from models import user_model
from middlewares.error_middleware import setup_exception_handlers

print("Server startup: Initializing components...")
print("Creating database tables...📑")
user_model.Base.metadata.create_all(bind=engine)
print("Database tables created.✅")


app = FastAPI()
app.add_middleware(SecurityMiddleware)
setup_exception_handlers(app)

#--- Include Routers ---
app.include_router(auth_routes.router)
app.include_router(user_routes.user_router)
app.include_router(process_routes.process_router)

@app.get("/")
async def root():
    return {"Title": "Welcome to real estate API"}
