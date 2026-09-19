import os
from agent.plugins.base import BasePlugin

class SSHHardeningPlugin(BasePlugin):
    check_id = "SSH_HARDENING"
    name = "SSH Remote Access Hardening"

    def run(self) -> dict:
        config_path = "/etc/ssh/sshd_config"
        raw_evidence = {"config_path": config_path, "exists": os.path.exists(config_path)}

        if not os.path.exists(config_path):
            return {
                "check_id": self.check_id,
                "status": "PASS",
                "details": "SSH service config not present (SSH daemon disabled).",
                "raw_evidence": raw_evidence,
                "evidence_hash": self.compute_evidence_hash(raw_evidence)
            }

        try:
            with open(config_path, "r") as f:
                lines = f.readlines()

            permit_root = True
            password_auth = True

            for line in lines:
                line = line.strip()
                if line.startswith("#"):
                    continue
                if "PermitRootLogin no" in line:
                    permit_root = False
                if "PasswordAuthentication no" in line:
                    password_auth = False

            raw_evidence["PermitRootLogin_Disabled"] = not permit_root
            raw_evidence["PasswordAuthentication_Disabled"] = not password_auth

            if not permit_root and not password_auth:
                status, details = "PASS", "SSH hardened: Root login and Password Auth disabled."
            else:
                status, details = "FAIL", f"SSH hardening incomplete (PermitRootLogin: {permit_root}, PasswordAuth: {password_auth})."

        except Exception as e:
            status = "WARNING"
            details = f"Could not read SSH config: {e}"
            raw_evidence["error"] = str(e)

        return {
            "check_id": self.check_id,
            "status": status,
            "details": details,
            "raw_evidence": raw_evidence,
            "evidence_hash": self.compute_evidence_hash(raw_evidence)
        }
