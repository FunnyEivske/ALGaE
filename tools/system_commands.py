import subprocess
import platform

def restart_algae_service():
    """Restarts the AI system (Linux only)."""
    if platform.system() == "Linux":
        subprocess.run(["sudo", "systemctl", "restart", "algae-ai.service"])
        return "Restarting now."
    return "Not on a Linux system."

def get_system_temp():
    """Gets CPU temperature to make sure the Lenovo M70q isn't overheating."""
    if platform.system() == "Linux":
        try:
            temp = subprocess.check_output(["cat", "/sys/class/thermal/thermal_zone0/temp"])
            return f"CPU Temperature is {int(temp) / 1000}°C"
        except:
            return "Could not read temperature sensors."
    return "Temperature monitoring not supported on this OS."