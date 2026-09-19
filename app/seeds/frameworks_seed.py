from app.models import db
from app.models.framework import Framework, Control, CheckDefinition, ControlCheckMapping

def seed_frameworks_and_controls():
    """Seeds ISO 27001:2022, SOC 2 Type II, NIST CSF 2.0, and CIS v8 controls into database."""
    
    # 1. Framework Definitions
    frameworks_data = [
        {
            "code": "ISO_27001_2022",
            "name": "ISO/IEC 27001:2022",
            "version": "2022",
            "description": "International Standard for Information Security Management Systems (ISMS)."
        },
        {
            "code": "SOC2_TYPE2",
            "name": "SOC 2 Type II",
            "version": "2017",
            "description": "AICPA Trust Services Criteria for Security, Availability, and Confidentiality."
        },
        {
            "code": "NIST_CSF_2",
            "name": "NIST Cybersecurity Framework 2.0",
            "version": "2.0",
            "description": "NIST Framework for improving critical infrastructure cybersecurity."
        },
        {
            "code": "CIS_CONTROLS_V8",
            "name": "CIS Critical Security Controls v8",
            "version": "8.0",
            "description": "Center for Internet Security prioritized set of safeguard actions."
        }
    ]

    framework_map = {}
    for fw in frameworks_data:
        existing = Framework.query.filter_by(code=fw["code"]).first()
        if not existing:
            existing = Framework(**fw)
            db.session.add(existing)
            db.session.flush()
        framework_map[fw["code"]] = existing

    # 2. Control Definitions per Framework
    controls_data = [
        # ISO 27001:2022 Controls
        {
            "framework_code": "ISO_27001_2022",
            "control_code": "A.8.20",
            "title": "Network Security",
            "category": "Technological Controls",
            "description": "Networks and network devices shall be secured, managed, and controlled."
        },
        {
            "framework_code": "ISO_27001_2022",
            "control_code": "A.8.24",
            "title": "Use of Cryptography",
            "category": "Technological Controls",
            "description": "Rules for the effective use of cryptography, including key management, shall be defined and implemented."
        },
        {
            "framework_code": "ISO_27001_2022",
            "control_code": "A.8.9",
            "title": "Configuration Management",
            "category": "Technological Controls",
            "description": "Configurations, including security configurations, of hardware, software, services and networks shall be established, documented, implemented, monitored and reviewed."
        },
        {
            "framework_code": "ISO_27001_2022",
            "control_code": "A.8.7",
            "title": "Protection Against Malware",
            "category": "Technological Controls",
            "description": "Protection against malware shall be implemented and supported by appropriate user awareness."
        },

        # SOC 2 Type II Controls
        {
            "framework_code": "SOC2_TYPE2",
            "control_code": "CC6.6",
            "title": "Boundary Protection & Firewall Enforcement",
            "category": "Common Criteria - Logical and Physical Access Controls",
            "description": "Logical access security measures are implemented to restrict boundary interfaces."
        },
        {
            "framework_code": "SOC2_TYPE2",
            "control_code": "CC6.7",
            "title": "Transmission & Storage Encryption",
            "category": "Common Criteria - Logical and Physical Access Controls",
            "description": "Data at rest and in transit is protected using cryptographic algorithms."
        },
        {
            "framework_code": "SOC2_TYPE2",
            "control_code": "CC6.1",
            "title": "Access & Hardening Management",
            "category": "Common Criteria - Logical and Physical Access Controls",
            "description": "Infrastructure access is hardened and constrained to authorized principals."
        },
        {
            "framework_code": "SOC2_TYPE2",
            "control_code": "CC6.8",
            "title": "Malware Detection & Endpoint Protection",
            "category": "Common Criteria - Logical and Physical Access Controls",
            "description": "Prevention of unauthorized or malicious software execution on system endpoints."
        },

        # NIST CSF 2.0 Controls
        {
            "framework_code": "NIST_CSF_2",
            "control_code": "PR.IR-01",
            "title": "Infrastructure Resilience & Boundary Defense",
            "category": "Protect - Infrastructure Resilience",
            "description": "Networks and environment boundaries are protected against unauthorized access."
        },
        {
            "framework_code": "NIST_CSF_2",
            "control_code": "PR.DS-01",
            "title": "Data Security & Disk Encryption",
            "category": "Protect - Data Security",
            "description": "Data at rest is protected with robust encryption controls."
        },
        {
            "framework_code": "NIST_CSF_2",
            "control_code": "PR.AA-01",
            "title": "Identity & Remote Access Hardening",
            "category": "Protect - Access Control",
            "description": "Remote administrative access interfaces are hardened and authentication is restricted."
        },

        # CIS v8 Controls
        {
            "framework_code": "CIS_CONTROLS_V8",
            "control_code": "CIS-4.4",
            "title": "Enforce Network Firewalls on Endpoints",
            "category": "Control 04: Secure Configuration of Enterprise Assets",
            "description": "Configure automatic host-based firewalls on all enterprise endpoints."
        },
        {
            "framework_code": "CIS_CONTROLS_V8",
            "control_code": "CIS-3.11",
            "title": "Encrypt Sensitive Data at Rest",
            "category": "Control 03: Data Protection",
            "description": "Encrypt data at rest on enterprise assets using full disk encryption."
        },
        {
            "framework_code": "CIS_CONTROLS_V8",
            "control_code": "CIS-10.1",
            "title": "Deploy Anti-Malware / EDR Software",
            "category": "Control 10: Malware Defenses",
            "description": "Deploy and maintain anti-malware and EDR software across enterprise endpoints."
        }
    ]

    control_map = {}
    for c in controls_data:
        fw_code = c.pop("framework_code")
        fw = framework_map.get(fw_code)
        if not fw:
            continue
        existing = Control.query.filter_by(framework_id=fw.id, control_code=c["control_code"]).first()
        if not existing:
            existing = Control(framework_id=fw.id, **c)
            db.session.add(existing)
            db.session.flush()
        control_map[f"{fw_code}:{c['control_code']}"] = existing

    # 3. CheckDefinitions (Technical Telemetry Checks)
    check_defs_data = [
        {
            "check_id": "FIREWALL_ACTIVE",
            "name": "Host Firewall Active Enforcement",
            "description": "Validates that host OS firewall (UFW, Windows Firewall, macOS ALF) is active.",
            "severity": "CRITICAL"
        },
        {
            "check_id": "DISK_ENCRYPTION",
            "name": "Full Disk Encryption Enforcement",
            "description": "Validates that host volume encryption (LUKS, BitLocker, FileVault) is enabled.",
            "severity": "HIGH"
        },
        {
            "check_id": "SSH_HARDENING",
            "name": "SSH Remote Access Hardening",
            "description": "Ensures root login and plain password authentication are disabled for SSH.",
            "severity": "HIGH"
        },
        {
            "check_id": "EDR_RUNNING",
            "name": "EDR / Antivirus Protection Running",
            "description": "Validates that an approved EDR or Antivirus daemon is active on the endpoint.",
            "severity": "CRITICAL"
        }
    ]

    check_def_map = {}
    for cd in check_defs_data:
        existing = CheckDefinition.query.filter_by(check_id=cd["check_id"]).first()
        if not existing:
            existing = CheckDefinition(**cd)
            db.session.add(existing)
            db.session.flush()
        check_def_map[cd["check_id"]] = existing

    # 4. Multi-Framework Mappings (Cross-map 1 Check to Multiple Framework Controls)
    mappings_matrix = [
        ("FIREWALL_ACTIVE", ["ISO_27001_2022:A.8.20", "SOC2_TYPE2:CC6.6", "NIST_CSF_2:PR.IR-01", "CIS_CONTROLS_V8:CIS-4.4"]),
        ("DISK_ENCRYPTION", ["ISO_27001_2022:A.8.24", "SOC2_TYPE2:CC6.7", "NIST_CSF_2:PR.DS-01", "CIS_CONTROLS_V8:CIS-3.11"]),
        ("SSH_HARDENING", ["ISO_27001_2022:A.8.9", "SOC2_TYPE2:CC6.1", "NIST_CSF_2:PR.AA-01"]),
        ("EDR_RUNNING", ["ISO_27001_2022:A.8.7", "SOC2_TYPE2:CC6.8", "CIS_CONTROLS_V8:CIS-10.1"])
    ]

    for check_id, target_control_keys in mappings_matrix:
        check_def = check_def_map.get(check_id)
        if not check_def:
            continue
        for key in target_control_keys:
            ctrl = control_map.get(key)
            if not ctrl:
                continue
            existing_mapping = ControlCheckMapping.query.filter_by(
                check_definition_id=check_def.id,
                control_id=ctrl.id
            ).first()
            if not existing_mapping:
                mapping = ControlCheckMapping(check_definition_id=check_def.id, control_id=ctrl.id)
                db.session.add(mapping)

    db.session.commit()
    print("[+] GRC Multi-Framework Engine database seeded successfully!")
