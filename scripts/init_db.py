import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.core.init_db import init_database

if __name__ == "__main__":
    print("Initializing Digital Twin Database...")
    init_database()
    print("✅ Database initialized successfully.")
