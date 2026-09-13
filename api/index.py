import sys
import os

# Menambahkan root directory backend ke dalam path agar Python bisa mengenali folder 'app'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# This file acts as the entrypoint for Vercel Serverless Functions.
# Vercel will automatically detect this and run the FastAPI app.