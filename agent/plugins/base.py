import json
import hashlib

class BasePlugin:
    """
    Abstract Base Class for Agent 2.0 system check plugins.
    Each plugin implements run() and computes cryptographic SHA-256 evidence hashes.
    """
    check_id = "GENERIC_CHECK"
    name = "Generic Check Plugin"

    def compute_evidence_hash(self, raw_evidence: dict) -> str:
        """Computes SHA-256 hash over deterministic JSON representation of evidence."""
        serialized = json.dumps(raw_evidence, sort_keys=True).encode('utf-8')
        return hashlib.sha256(serialized).hexdigest()

    def run(self) -> dict:
        """
        Executes the check. Must return dictionary format:
        {
            "check_id": self.check_id,
            "status": "PASS" | "FAIL" | "WARNING",
            "details": "Explanation message",
            "raw_evidence": {...},
            "evidence_hash": "sha256_hash_string"
        }
        """
        raise NotImplementedError("Plugins must implement run()")
