from os import getenv
from pathlib import Path

ROOT = Path(__file__).parent

usr_dir = getenv("PLAYWRIGHT_USR_DIR", str(ROOT.parent / 'user_dir'))

user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0.0.0 Safari/537.36"
)
