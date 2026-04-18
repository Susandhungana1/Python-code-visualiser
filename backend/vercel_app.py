# Vercel Python Runtime Entry Point
# This file is used by Vercel's Python runtime

from main import app

# Vercel expects an "app" variable for ASGI
handler = app