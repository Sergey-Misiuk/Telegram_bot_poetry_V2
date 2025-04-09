import os
from dotenv import load_dotenv
from typing import Optional


load_dotenv()


DB_URL: Optional[str] = str(os.environ.get("DATABASE_URL"))
SECRET_KEY: Optional[str] = str(os.environ.get("SECRET_KEY"))
TG_KEY_API: Optional[str] = str(os.environ.get("API_KEY"))
