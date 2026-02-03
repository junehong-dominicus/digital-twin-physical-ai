import os
import shutil

def main():
    # Get the directory where this script (and main.py) is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the target directory expected by main.py
    target_dir = os.path.join(base_dir, "visualization", "viewer")
    
    # Files to move
    files_to_move = ["index.html", "style.css", "app.js"]
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Created directory: {target_dir}")
        
    for filename in files_to_move:
        src = os.path.join(base_dir, filename)
        dst = os.path.join(target_dir, filename)
        
        if os.path.exists(src):
            shutil.move(src, dst)
            print(f"Moved {filename} to {target_dir}")
        elif os.path.exists(dst):
            print(f"{filename} already exists in {target_dir}")
        else:
            print(f"Warning: {filename} not found in root directory.")

if __name__ == "__main__":
    main()