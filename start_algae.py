import os
import subprocess

# Project Setup Variables
GITHUB_REPO = "https://github.com/FunnyEivske/ALGaE.git"
PROJECT_FOLDER = os.path.expanduser("~/ALGaE")
MEMORY_FOLDER = os.path.expanduser("~/.algae_data")
VENV_PATH = os.path.join(PROJECT_FOLDER, "venv")

def run_terminal_command(command, cwd=None):
    print(f"Executing: {command}")
    subprocess.run(command, shell=True, check=True, cwd=cwd)

def prepare_environment():
    print("Initializing ALGaE System...")

    # Create memory folder
    if not os.path.exists(MEMORY_FOLDER):
        print(f"Making memory directory at {MEMORY_FOLDER}")
        os.makedirs(MEMORY_FOLDER)

    # Download or update code
    if not os.path.exists(PROJECT_FOLDER):
        print("Downloading code from GitHub...")
        run_terminal_command(f"git clone {GITHUB_REPO} {PROJECT_FOLDER}")
    else:
        print("Updating existing code...")
        run_terminal_command("git pull origin main", cwd=PROJECT_FOLDER)

    # Setup Python environment
    if not os.path.exists(VENV_PATH):
        print("Building Python environment...")
        run_terminal_command(f"python3.11 -m venv {VENV_PATH}")

    # Check and Install dependencies
    python_pip = os.path.join(VENV_PATH, "bin", "pip")
    requirements_file = os.path.join(PROJECT_FOLDER, "requirements.txt")
    if os.path.exists(requirements_file):
        print("Checking for missing or new dependencies to install...")
        run_terminal_command(f"{python_pip} install -r {requirements_file}")

def boot_algae():
    print("Booting ALGaE Modules...")
    python_executable = os.path.join(VENV_PATH, "bin", "python")
    
    # 1. Start the visual interface server
    server_script = os.path.join(PROJECT_FOLDER, "server.py")
    subprocess.Popen([python_executable, server_script], cwd=PROJECT_FOLDER)
    
    # 2. Start the display
    subprocess.Popen("startx /usr/bin/chromium-browser --kiosk http://localhost:8080 --no-sandbox", shell=True)

    # 3. Start the AI core
    brain_script = os.path.join(PROJECT_FOLDER, "core", "ai_main.py")
    subprocess.run([python_executable, brain_script], cwd=PROJECT_FOLDER)

if __name__ == "__main__":
    try:
        prepare_environment()
        boot_algae()
    except Exception as error:
        print(f"System failed to boot: {error}")