import platform
import subprocess

def check_disk_encryption():
    system = platform.system()
    try:
        if system == "Darwin":
            result = subprocess.run(["fdesetup", "status"], capture_output=True, text=True, timeout=5)
            if "FileVault is On" in result.stdout:
                return "PASS", "FileVault disk encryption is enabled."
            return "FAIL", "FileVault disk encryption is disabled."
        elif system == "Windows":
            result = subprocess.run(["manage-bde", "-status"], capture_output=True, text=True, timeout=5)
            if "Protection On" in result.stdout:
                return "PASS", "BitLocker protection is enabled."
            return "FAIL", "BitLocker protection is disabled."
        elif system == "Linux":
            result = subprocess.run(["lsblk", "-o", "FSTYPE"], capture_output=True, text=True, timeout=5)
            if "crypto_LUKS" in result.stdout:
                return "PASS", "LUKS encrypted partition detected."
            return "WARNING", "No LUKS encrypted partition found."
        else:
            return "WARNING", f"Disk encryption check not supported on {system}."
    except Exception as e:
        return "WARNING", f"Could not determine disk encryption status: {e}"
