import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

def load_env(file_path: str='.env'):
    if not os.path.exists(file_path):
        return

    with open(file_path) as fenv:
        for line in fenv:
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            key, value = line.split('=', 1)
            os.environ[key] = value

load_env(BASE_DIR / '.env')

class Settings:
    app_name: str = os.getenv('APP_NAME', default='AMS')

    server_host: str = os.getenv('SERVER_HOST', default='127.0.0.1')
    server_port: int = int(os.getenv('SERVER_PORT', default="8000"))

    db_name: str = os.getenv('DB_NAME', default='ams.db')


settings = Settings()