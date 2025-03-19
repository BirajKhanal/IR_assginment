import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get individual database settings
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Construct the DATABASE_URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Ensure all required values exist
if not all([DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT]):
    raise ValueError(
        "One or more required database environment variables are missing!"
    )
