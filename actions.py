
import subprocess


def run_script(script_path):
    """Run an external script."""
    try:
        subprocess.run(["python", script_path], check=True)
    except Exception as e:
        print(f"Error running script: {e}")


def send_notification(message):
    """Send a desktop notification."""
    print(f"Notification: {message}")
