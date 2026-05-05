import pytest
import subprocess
import time
import sys
import os
import io

@pytest.fixture(scope="session", autouse=True)
def run_server():
    # Start the server
    # We assume tests are run from the project root where main.py resides
    cwd = os.getcwd()
    server_process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(2)
    
    yield
    
    # Stop the server
    server_process.terminate()
    try:
        server_process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        server_process.kill()
