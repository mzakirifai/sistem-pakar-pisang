"""Konfigurasi koneksi database, dibaca dari file .env."""

import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST: str = os.getenv("DB_HOST", "localhost")
DB_USER: str = os.getenv("DB_USER", "root")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
DB_NAME: str = os.getenv("DB_NAME", "sistem_pakar_pisang")
DB_PORT: int = int(os.getenv("DB_PORT", "3306"))