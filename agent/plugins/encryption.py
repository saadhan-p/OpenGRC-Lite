import platform
import subprocess
from agent.plugins.base import BasePlugin

class DiskEncryptionPlugin(BasePlugin):
    check_id = "DISK_ENCRYPTION"
    name = "Full Disk Encryption Enforcement"

    def run(self) -> dict:
        system = platform.system()
        status = "WARNING"
        details = f"Disk encryption check not supported on {system}."
        raw_evidence = {"os": system, "output": None}

        try:
            if system == "Darwin":
                res = subprocess.run(["fdesetup", "status"], capture_output=True, text=True, timeout=5)
                raw_evidence["output"] = res.stdout.strip()
                if "FileVault is On" in res.stdout:
                    status, details = "PASS", "FileVault disk encryption is enabled."
                else:
                    status, details = "FAIL", "FileVault disk encryption is disabled."
            elif system == "Windows":
                res = subprocess.run(["manage-bde", "-status"], capture_output=True, text=True, timeout=5)
                raw_evidence["output"] = res.stdout.strip()
                if "Protection On" in res.stdout:
                    status, details = "PASS", "BitLocker protection is enabled."
                else:
                    status, details = "FAIL", "BitLocker protection is disabled."
            elif system == "Linux":
                res = subprocess.run(["lsblk", "-o", "FSTYPE"], capture_output=True, text=True, timeout=5)
                raw_evidence["output"] = res.stdout.strip()
                if "crypto_LUKS" in res.stdout:
                    status, details = "PASS", "LUKS encrypted partition detected."
                else:
                    status, details = "WARNING", "No LUKS encrypted partition found."
        except Exception as e:
            status = "WARNING"
            details = f"Could not determine disk encryption status: {e}"
            raw_evidence["error"] = str(e)

        return {
            "check_id": self.check_id,
            "status": status,
            "details": details,
            "raw_evidence": raw_evidence,
            "evidence_hash": self.compute_evidence_hash(raw_evidence)
        }
