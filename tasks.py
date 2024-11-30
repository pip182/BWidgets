
import psutil
import subprocess


def check_ping(host):
    """Check ping latency to a host."""
    try:
        response = subprocess.run(
            ["ping", "-c", "1", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=2
        )
        return (
            f"Ping to {host}: "
            f"{response.stdout.decode().split('time=')[1].split(' ')[0]}"
        )
    except Exception as e:
        return f"Error: {e}"


def get_system_usage():
    """Return system CPU and memory usage."""
    return {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
    }
