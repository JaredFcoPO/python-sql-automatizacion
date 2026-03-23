from dotenv import load_dotenv
import os

load_dotenv()
usuario = os.getenv("USER")
contrasena = os.getenv("PASSWORD")
dns = os.getenv("dns")