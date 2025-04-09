import os
from dotenv import load_dotenv
from typing import Optional


load_dotenv()


BOT_TOKEN: Optional[str] = str(os.environ.get("BOT_TOKEN"))
DB_URL: Optional[str] = str(os.environ.get("DATABASE_URL"))
ADMIN: Optional[str] = str(os.environ.get("ADMIN_ID"))
API_BASE_URL: Optional[str] = str(os.environ.get("API_BASE_URL"))
TG_KEY_API: Optional[str] = str(os.environ.get("API_KEY"))
