import os

from constants import VECTORDB_FILE_PATH
from getfiles import CanvasDownloader

CANVAS_API_KEY = os.environ.get("CANVAS_API_KEY")
CANVAS_API_URL = "canvas.ubc.ca"

API = CanvasDownloader(CANVAS_API_URL, CANVAS_API_KEY, VECTORDB_FILE_PATH)
API.download_files(False, "both")
