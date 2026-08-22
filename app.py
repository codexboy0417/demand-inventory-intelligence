"""
Project FORESIGHT — Root App Entry Point
Launches the 7-Page Streamlit Planning Dashboard.
"""
import subprocess
import sys
import os

def main():
    app_path = os.path.join(os.path.dirname(__file__), 'app', 'main.py')
    print("Starting Project FORESIGHT Streamlit Dashboard...")
    print(f"Path: {app_path}")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

if __name__ == '__main__':
    main()
