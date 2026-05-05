import subprocess
import sys
import time
import os
import signal

def run_command(command, name):
    """Starts a subprocess and returns the process object."""
    print(f"🚀 Starting {name}...")
    # Use 'uv run' to ensure the correct environment is used
    full_cmd = ["uv", "run"] + command
    return subprocess.Popen(
        full_cmd,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

def main():
    processes = []
    
    # 1. Start Simulator (Industrial Environment)
    # Port 8081 for Simulator Dashboard, 5020 for Modbus, etc.
    processes.append((run_command([sys.executable, "simulator/main.py"], "Industrial Protocol Simulator"), "SIMULATOR"))
    
    # Wait a moment for MQTT broker and servers to initialize
    time.sleep(2)
    
    # 2. Start Persistence Worker (MQTT-to-DB Bridge)
    processes.append((run_command([sys.executable, "backend/core/persistence_worker.py"], "Persistence Worker"), "PERSISTENCE"))
    
    # 3. Start Backend API Server
    # Port 8001 for Digital Twin API and Phase 2 Dashboard
    processes.append((run_command(["uvicorn", "backend.api.main:app", "--port", "8001", "--no-access-log"], "Digital Twin API Server"), "API"))

    print("\n" + "="*50)
    print("🌟 DIGITAL TWIN PHYSICAL AI SYSTEM IS ONLINE")
    print("="*50)
    print("🔗 Simulator Dashboard:  http://localhost:8081/dashboard")
    print("🔗 Digital Twin API:     http://localhost:8001")
    print("🔗 Phase 2 UI (If avail): http://localhost:8001/dashboard/")
    print("="*50)
    print("Press CTRL+C to shut down all components...\n")

    try:
        # Monitor processes and stream output
        while True:
            for proc, name in processes:
                # Check if process died
                if proc.poll() is not None:
                    print(f"❌ {name} process has stopped unexpectedly!")
                    sys.exit(1)
                
                # Non-blocking check for output (optional, keeping it simple here)
                # In a real tool, we might want to pipe logs to files
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down system...")
        for proc, name in processes:
            print(f"Terminating {name}...")
            # On Windows, we might need taskkill or similar if Popen.terminate() is too gentle
            if os.name == 'nt':
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(proc.pid)], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                proc.terminate()
        print("✅ All processes stopped.")

if __name__ == "__main__":
    main()
