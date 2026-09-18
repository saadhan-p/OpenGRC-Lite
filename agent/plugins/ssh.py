import os

def check_ssh_config():
    config_path = "/etc/ssh/sshd_config"
    if not os.path.exists(config_path):
        return "WARNING", "SSH configuration file not found."

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

        if not permit_root and not password_auth:
            return "PASS", "SSH hardened: Root login and Password Auth disabled."
        else:
            return "FAIL", f"SSH hardening incomplete (RootLogin: {permit_root}, PasswordAuth: {password_auth})."
    except Exception as e:
        return "WARNING", f"Could not read SSH config: {e}"
