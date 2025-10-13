#!/usr/bin/env python3
"""
WSGI entry point for the Web Spelling Quiz application
For deployment with Apache mod_wsgi or other WSGI servers
"""

import os
import sys

# Add your project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_quiz import app, init_db

# Initialize database on startup
init_db()

# WSGI application object
application = app

if __name__ == "__main__":
    application.run()