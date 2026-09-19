import platform
import subprocess
from agent.plugins.base import BasePlugin

class FirewallPlugin(BasePlugin):
    check_id = "FIREWALL_ACTIVE"
    name = "Host Firewall Active Enforcement"

    def run(self) -> dict:
        system = platform.system()
        status = "WARNING"
        details = f"No firewall check implemented for {system}."
        raw_evidence = {"os": system, "command_output": None}

        try:
            if system == "Linux":
                res = subprocess.run(["ufw", "status"], capture_output=True, text=True, timeout=5)
                raw_evidence["command_output"] = res.stdout.strip()
                if "Status: active" in res.stdout:
                    status, details = "PASS", "Linux Firewall (ufw) is active."
                else:
                    status, details = "FAIL", "CRITICAL: Linux Firewall (ufw) is inactive."
            elif system == "Windows":
                res = subprocess.run(
                    ["netsh", "advfirewall", "show", "currentprofile"],
                    capture_output=True, text=True, timeout=5
                )
                raw_evidence["command_output"] = res.stdout.strip()
                if "State                                 ON" in res.stdout:
                    status, details = "PASS", "Windows Firewall is active."
                else:
                    status, details = "FAIL", "CRITICAL: Windows Firewall is off."
            elif system == "Darwin":
                res = subprocess.run(
                    ["defaults", "read", "/Library/Preferences/com.apple.alf", "globalstate"],
                    capture_output=True, text=True, timeout=5
                )
                raw_evidence["command_output"] = res.stdout.strip()
                if res.stdout.strip() in ("1", "2"):
                    status, details = "PASS", "macOS Application Firewall is active."
                else:
                    status, details = "FAIL", "CRITICAL: macOS Application Firewall is off."
        except Exception as e:
            status = "WARNING"
            details = f"Could not determine firewall status: {e}"
            raw_evidence["error"] = str(e)

        return {
            "check_id": self.check_id,
            "status": status,
            "details": details,
            "raw_evidence": raw_evidence,
            "evidence_hash": self.compute_evidence_hash(raw_evidence)
        }
