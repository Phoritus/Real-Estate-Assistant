from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from html_content import HTML_CONTENT
try:
    from fastapi_fortify import SecurityMiddleware
    _SECURITY_AVAILABLE = True
except Exception:
    SecurityMiddleware = None  # type: ignore
    _SECURITY_AVAILABLE = False
from fastapi.middleware.cors import CORSMiddleware
from router import auth_routes, user_routes, process_routes
from database.postgresdb import engine
from models import user_model
from middlewares.error_middleware import setup_exception_handlers
from env import PORT, DEV_PORT

# print("Server startup: Initializing components...")
# print("Creating database tables...📑")
# user_model.Base.metadata.create_all(bind=engine)
# print("Database tables created.✅")

origin = [
    DEV_PORT
    
]

app = FastAPI()
if _SECURITY_AVAILABLE and SecurityMiddleware:
    app.add_middleware(SecurityMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
setup_exception_handlers(app)

#--- Include Routers ---
app.include_router(auth_routes.router)
app.include_router(user_routes.user_router)
app.include_router(process_routes.process_router)

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_CONTENT


if __name__ == "__main__":
    import uvicorn
    port = int(PORT)
    uvicorn.run("main:app", host="0.0.0.0", port=port)