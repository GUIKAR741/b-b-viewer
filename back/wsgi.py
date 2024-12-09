"""."""
import os
from app import start_app

os.environ["FLASK_APP"] = "app:start_app"
os.environ["FLASK_SKIP_DOTENV"] = "1"
app = start_app()