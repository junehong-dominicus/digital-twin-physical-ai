import uvicorn
import os

def main():
    """
    Launches the FastAPI server using uvicorn.
    Reads host and port from environment variables, with sensible defaults.
    """
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8001))

    print(f"Starting Digital Twin API server at http://{host}:{port}")
    print(f"Dashboard available at http://{host}:{port}/dashboard/")

    uvicorn.run("main:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    main()