import os
from dotenv import load_dotenv

env_name = os.environ.get("NODE_ENV", "development")
env_file = f".env.{env_name}.local"

load_dotenv(dotenv_path=env_file)
PORT = os.environ.get("PORT")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DB_URL = os.environ.get("DATABASE_URL")