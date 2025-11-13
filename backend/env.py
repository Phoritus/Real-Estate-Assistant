import os
from dotenv import load_dotenv

env_name = os.environ.get("NODE_ENV", "development")
env_file = f".env.{env_name}.local"

load_dotenv(dotenv_path=env_file)
PORT = os.environ.get("PORT")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DB_URL = os.environ.get("DATABASE_URL")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
JWT_EXPIRATION_TIME = int(os.environ.get("JWT_EXPIRATION_TIME", 1))