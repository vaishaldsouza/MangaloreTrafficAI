# run_api.py
import uvicorn
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

if __name__ == "__main__":
    print("Starting Mangalore Traffic AI Backend...")
    print("API Documentation available at: http://localhost:8000/docs")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
