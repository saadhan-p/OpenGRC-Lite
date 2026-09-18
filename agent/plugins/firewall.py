import platform
import subprocess

def check_firewall():
    system = platform.system()
    try:
        if system == "Linux":
            result = subprocess.run(["ufw", "status"], capture_output=True, text=True, timeout=5)
            if "Status: active" in result.stdout:
                return "PASS", "Firewall (ufw) is active."
            return "FAIL", "CRITICAL: Firewall (ufw) is inactive."
        elif system == "Windows":
            result = subprocess.run(
                ["netsh", "advfirewall", "show", "currentprofile"],
                capture_output=True, text=True, timeout=5
            )
            if "State                                 ON" in result.stdout:
                return "PASS", "Windows Firewall is active."
            return "FAIL", "CRITICAL: Windows Firewall is off."
        elif system == "Darwin":
            result = subprocess.run(
                ["defaults", "read", "/Library/Preferences/com.apple.alf", "globalstate"],
                capture_output=True, text=True, timeout=5
            )
            if result.stdout.strip() in ("1", "2"):
                return "PASS", "macOS Application Firewall is active."
            return "FAIL", "CRITICAL: macOS Application Firewall is off."
        else:
            return "WARNING", f"No firewall check implemented for {system}."
    except Exception as e:
        return "WARNING", f"Could not determine firewall status: {e}"
