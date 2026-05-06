import subprocess
import sys
import os
import shutil

def build_executables():
    print("--- Orex-i AI Tool Builder ---")
    
    # Ensure PyInstaller is available
    try:
        import PyInstaller
    except ImportError:
        print("Error: PyInstaller not found. Please run 'uv pip install pyinstaller'")
        return

    scripts = [
        "field_data_generator.py",
        "model_ota_cli.py"
    ]

    dest_folder = os.path.join('..', 'exe')
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    for script in scripts:
        if not os.path.exists(script):
            print(f"Error: {script} not found!")
            continue

        print(f"\nBuilding {script}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--clean",
                script
            ])
            print(f"Successfully built {script}")

            # Copy to ../exe folder
            exe_name = script.replace('.py', '.exe')
            src_path = os.path.join('dist', exe_name)
            dest_path = os.path.join(dest_folder, exe_name)

            if os.path.exists(src_path):
                print(f"Copying {exe_name} to {dest_folder}...")
                shutil.copy2(src_path, dest_path)
                print("Copy complete.")
            else:
                print(f"Error: {src_path} not found.")

        except subprocess.CalledProcessError as e:
            print(f"Failed to build {script}: {e}")

    print("\n--- Build Complete ---")
    print("Executables are located in the 'dist' folder and copied to '../exe'.")

if __name__ == "__main__":
    build_executables()
