import os
import shutil
import subprocess

APP_NAME = "TrackMenuBar"
PROJECT_DIR = os.path.expanduser("~/Desktop/track")  # Change if needed
DIST_DIR = os.path.join(PROJECT_DIR, "dist")
BUILD_DIR = os.path.join(PROJECT_DIR, "build")
APP_BUNDLE = os.path.join(DIST_DIR, f"{APP_NAME}.app")
INSTALL_DIR = "/Applications"


def install_dependencies():
    """Ensure py2app and dependencies are installed with PEP 517."""
    print("📦 Installing dependencies...")
    subprocess.run(["python", "-m", "pip", "install", "--upgrade", "setuptools", "wheel", "py2app"], check=True)


def build_app():
    """Run py2app using pyproject.toml, ensuring a clean build."""
    print("🚀 Cleaning old build files...")

    # 🔹 Ensure build and dist directories are completely removed
    for path in [BUILD_DIR, DIST_DIR]:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)

    print("🚀 Building macOS app with py2app...")

    # 🔹 Use PEP 517-compliant build command
    subprocess.run(["python", "setup.py", "py2app"], cwd=PROJECT_DIR, check=True)


def install_app():
    """Move the .app to /Applications and add it to startup."""
    print(f"📦 Moving app to {INSTALL_DIR}...")
    shutil.rmtree(os.path.join(INSTALL_DIR, f"{APP_NAME}.app"), ignore_errors=True)
    shutil.move(APP_BUNDLE, INSTALL_DIR)

    # Ensure macOS recognizes the app update
    print("🔄 Resetting macOS LaunchServices cache...")
    subprocess.run(["killall", "Dock"], check=True)
    subprocess.run(["killall", "SystemUIServer"], check=True)

    # Add to startup
    print("🔄 Adding to startup (hidden)...")
    subprocess.run([
        "osascript", "-e",
        f'tell application "System Events" to make login item at end with properties {{name:"{APP_NAME}", path:"{INSTALL_DIR}/{APP_NAME}.app", hidden:true}}'
    ], check=True)

    print("✅ Done! TrackMenuBar is installed and hidden from the Dock.")


if __name__ == "__main__":
    install_dependencies()  # 🔹 Run only once at the start
    build_app()  # 🔹 Build only once
    install_app()  # 🔹 Install the app once
