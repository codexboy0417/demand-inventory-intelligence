"""
Project FORESIGHT — Single Application Launcher
Executes the 7-Page Streamlit Planning Dashboard for NorthBay Living.
"""
import subprocess
import sys
import os

def main():
    app_path = os.path.join(os.path.dirname(__file__), 'app', 'main.py')
    print("Starting Project FORESIGHT Streamlit Dashboard...")
    print(f"Path: {app_path}")
    
    cmd = [sys.executable, "-m", "streamlit", "run", app_path]
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
